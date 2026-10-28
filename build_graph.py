import json
import re
from collections import defaultdict

# JSONファイルを読み込む
with open('slvsh_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ノードの頻度をカウント
node_freq = defaultdict(int)
# エッジの頻度をカウント (from -> to)
edge_freq = defaultdict(int)

# 各エントリを処理
for entry in data:
    components = entry.get('components', [])

    # 各components要素をカンマ、スラッシュ、スペースで分割して、フラットなリストにする
    all_elements = []
    for component in components:
        # カンマ、スラッシュ、スペースのいずれかで分割して、空白をトリム
        parts = [part.strip() for part in re.split(r'[,/\s]+', component)]
        all_elements.extend(parts)

    # ノードの頻度をカウント
    for element in all_elements:
        if element:  # 空文字列をスキップ
            node_freq[element] += 1

    # エッジの頻度をカウント（連続する要素間）
    for i in range(len(all_elements) - 1):
        from_node = all_elements[i].strip()
        to_node = all_elements[i + 1].strip()
        if from_node and to_node:  # 空文字列をスキップ
            edge_freq[(from_node, to_node)] += 1

# ノードリストを作成（freq順にソート）
nodes = [{"name": name, "freq": freq}
         for name, freq in sorted(node_freq.items(), key=lambda x: x[1], reverse=True)]

# エッジリストを作成（freq順にソート）
edges = [{"from": from_node, "to": to_node, "freq": freq}
         for (from_node, to_node), freq in sorted(edge_freq.items(), key=lambda x: x[1], reverse=True)]

# グラフデータを作成
graph_data = {
    "nodes": nodes,
    "edges": edges
}

# JSONファイルに出力
with open('slvsh_graph.json', 'w', encoding='utf-8') as f:
    json.dump(graph_data, f, ensure_ascii=False, indent=2)

print(f"グラフを作成しました: {len(nodes)}個のノード、{len(edges)}個のエッジ")
