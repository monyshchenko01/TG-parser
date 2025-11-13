import pandas as pd
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np

df = pd.read_csv("telegram_comments_korupcia_donaty.csv")
comments = df["comment_text"].dropna().drop_duplicates().tolist()

print("🚀 Завантажуємо модель...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

anchors_negative = [
    "я більше не буду донатити",
    "не бачу сенсу донатити після скандалу",
    "не довіряю волонтерам тепер",
    "після цього донатити не буду"
]

anchors_positive = [
    "я продовжую донатити",
    "підтримую армію попри скандали",
    "донати потрібні, не дивлячись ні на що",
    "продовжую допомагати армії"
]

print("🔢 Створюємо embeddings...")
embeddings = model.encode(comments, convert_to_tensor=True, show_progress_bar=True)
emb_neg = model.encode(anchors_negative, convert_to_tensor=True)
emb_pos = model.encode(anchors_positive, convert_to_tensor=True)

sim_neg = util.cos_sim(embeddings, emb_neg).mean(dim=1)
sim_pos = util.cos_sim(embeddings, emb_pos).mean(dim=1)

labels = (sim_pos > sim_neg).int().cpu().numpy()

df_clusters = pd.DataFrame({
    "comment_text": comments,
    "cluster": labels
})
df_clusters["cluster_label"] = df_clusters["cluster"].map({
    0: "не будуть донатити",
    1: "продовжують донатити"
})

df_clusters.to_csv("donate_clusters.csv", index=False, encoding="utf-8")
print("✅ Результати збережено у donate_clusters.csv")

print("🎨 Створюємо візуалізацію...")

pca = PCA(n_components=2)
points_2d = pca.fit_transform(embeddings.cpu().numpy())

colors = np.where(labels == 0, "red", "green")

plt.figure(figsize=(10, 7))
plt.scatter(points_2d[:, 0], points_2d[:, 1], c=colors, alpha=0.6, s=50)

plt.scatter(
    np.mean(points_2d[labels == 0, 0]), np.mean(points_2d[labels == 0, 1]),
    c="darkred", marker="x", s=200, label="Не донатять"
)
plt.scatter(
    np.mean(points_2d[labels == 1, 0]), np.mean(points_2d[labels == 1, 1]),
    c="darkgreen", marker="x", s=200, label="Продовжують донатити"
)

plt.title("💰 Класифікація коментарів про донати", fontsize=14)
plt.legend(fontsize=12)
plt.xlabel("PCA-вісь 1")
plt.ylabel("PCA-вісь 2")
plt.grid(alpha=0.2)
plt.show()

for cluster_id, label_name in [(0, "не будуть донатити"), (1, "продовжують донатити")]:
    print(f"\n🧩 {label_name.upper()}:")
    examples = df_clusters[df_clusters["cluster"] == cluster_id]["comment_text"].head(10).tolist()
    for ex in examples:
        print("  -", ex)
