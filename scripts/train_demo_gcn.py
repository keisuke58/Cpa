import argparse
import os
import io
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F


def build_demo_data(n: int, k: int, seed: int = 42):
    rng = np.random.default_rng(seed)
    centers = np.array([[0.15, 0.08, 0.35, 0.06],
                        [0.08, 0.12, 0.45, 0.09],
                        [0.20, 0.05, 0.30, 0.03],
                        [0.10, 0.09, 0.40, 0.08]], dtype=np.float64)
    lab = rng.integers(0, len(centers), size=n)
    X = centers[lab] + rng.normal(0.0, 0.02, size=(n, 4))
    X = np.clip(X, -0.2, 0.8).astype(np.float64)

    xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    sim = xn @ xn.T
    edges = []
    for i in range(n):
        idx = np.argsort(sim[i])[::-1]  # desc
        idx = [j for j in idx if j != i][:k]
        for j in idx:
            edges.append([i, j])
            edges.append([j, i])
    edge_index = np.array(edges, dtype=np.int64).T if edges else np.zeros((2, 0), dtype=np.int64)
    names = np.array([f"DEMO{i+1:04d}" for i in range(n)])
    return X.astype(np.float32), edge_index, names


class GCN(nn.Module):
    def __init__(self, in_dim: int, hidden: int, out_dim: int, src, dst, norm):
        super().__init__()
        self.W0 = nn.Linear(in_dim, hidden, bias=False)
        self.W1 = nn.Linear(hidden, out_dim, bias=False)
        self.dp = nn.Dropout(p=0.5)
        self.src = src
        self.dst = dst
        self.norm = norm

    def agg_once(self, H):
        S = self.W0(H)
        Z = torch.zeros_like(S)
        Z.index_add_(0, self.dst, S[self.src] * self.norm.unsqueeze(1))
        return Z

    def forward(self, X):
        H = F.relu(self.agg_once(X))
        H = self.dp(H)
        S = self.W1(H)
        Z = torch.zeros_like(S)
        Z.index_add_(0, self.dst, S[self.src] * self.norm.unsqueeze(1))
        return Z, H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="Number of demo nodes")
    ap.add_argument("--k", type=int, default=3, help="k-NN neighbors (bidirectional)")
    ap.add_argument("--hidden", type=int, default=64, help="Hidden dim")
    ap.add_argument("--epochs", type=int, default=200, help="Training epochs")
    ap.add_argument("--lr", type=float, default=1e-2, help="Learning rate")
    ap.add_argument("--outdir", type=str, default="outputs", help="Output directory")
    args = ap.parse_args()

    X, edge_index, names = build_demo_data(args.n, args.k)
    os.makedirs(args.outdir, exist_ok=True)

    # Standardize features
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True) + 1e-9
    Xn = (X - mu) / sd

    # Build normalized adjacency (with self-loop)
    n = X.shape[0]
    src = torch.tensor(edge_index[0], dtype=torch.long)
    dst = torch.tensor(edge_index[1], dtype=torch.long)
    loop_i = torch.arange(n, dtype=torch.long)
    src = torch.cat([src, loop_i], dim=0)
    dst = torch.cat([dst, loop_i], dim=0)
    deg = torch.zeros(n, dtype=torch.float32)
    deg.index_add_(0, src, torch.ones_like(src, dtype=torch.float32))
    deg.index_add_(0, dst, torch.ones_like(dst, dtype=torch.float32))
    deg = torch.clamp(deg, min=1.0)
    norm = 1.0 / torch.sqrt(deg[dst] * deg[src])

    Xin = torch.tensor(Xn, dtype=torch.float32)
    model = GCN(Xin.shape[1], args.hidden, Xin.shape[1], src, dst, norm)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=5e-4)

    print(f"[INFO] Training GCN on demo data: n={args.n}, k={args.k}, hidden={args.hidden}, epochs={args.epochs}")
    for ep in range(1, args.epochs + 1):
        model.train()
        opt.zero_grad()
        Z, H = model(Xin)
        loss = F.mse_loss(Z, Xin)
        loss.backward()
        opt.step()
        if ep == 1 or ep % 20 == 0 or ep == args.epochs:
            print(f"[EPOCH {ep:04d}] loss={loss.item():.6f}")

    # Save outputs
    Emb = H.detach().cpu().numpy()
    np.save(os.path.join(args.outdir, "demo_embeddings.npy"), Emb)
    np.savez(os.path.join(args.outdir, "demo_x_feature.npz"), x=X, tickers=names, feature_names=np.array(["op_margin","roe","equity_ratio","ocf_margin"]))
    np.save(os.path.join(args.outdir, "demo_edge_index.npy"), edge_index)
    print(f"[DONE] Saved embeddings and artifacts to: {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()

