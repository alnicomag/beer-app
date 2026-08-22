# Can Label Lab — Codex Handoff / Prototype 0

## 1. Project Overview

クラフトビール缶のラベルを物理的に剥がすことなく、缶を回転させながら撮影した画像・動画から、円筒表面のラベルデザインを平面展開画像として復元する。

最終的な製品像はスマートフォンアプリだが、現段階ではアプリ開発を目的としない。

Prototype 0 の目的は、理想的な撮影条件下において、

> **動画または連続画像から、実物のラベルを剥がして平面化・スキャンしたものに近い「鑑賞に耐える」展開画像を生成できるか**

を検証することである。

処理速度、リアルタイム性、自動缶検出、撮影UXなどは現段階では優先しない。

---

## 2. Primary Goal

最重要評価項目は **再構成画像の鑑賞品質** である。

画像処理アルゴリズムについては、現時点で有望と考えられる方式を可能な限り比較できる実験環境を構築する。

最初から特定アルゴリズムを正解と決めない。

単純な方式が十分な品質を達成する可能性も含め、各方式を同一条件で比較する。

---

## 3. Success Criteria

最終的には次の品質レベルを目標とする。

### Tier 1

主要な文字が読める。

### Tier 2

ラベルデザイン全体を問題なく鑑賞できる。

### Tier 3

継ぎ目や幾何学的歪みがほとんど気にならない。

### Tier 4

実物ラベルを剥がしてスキャンした画像と並べても、コレクション用途として十分満足できる。

Prototype 0 の最終目標は **Tier 4**。

---

## 4. Non-goals

Prototype 0 初期段階では以下を対象外とする。

- スマートフォンアプリ
- UI/UX
- 自動缶検出
- リアルタイム処理
- 撮影ガイド
- 手持ち撮影への対応
- 高速処理
- GPU最適化
- クラウド処理
- ビール情報管理
- コレクションDB
- AIによるラベル認識
- ビール名・ブルワリー名の自動認識

缶領域の指定など、本質ではない要素は手動でもよい。

---

## 5. Assumed Capture Conditions

初期検証では撮影条件は理想的であると仮定する。

想定条件:

- スマートフォンまたはカメラは固定
- 缶の回転軸はほぼ固定
- 缶は垂直
- カメラは缶中央付近へ正対
- 背景は単純
- 拡散光を使用
- 強い鏡面反射を避ける
- AE/AFは可能なら固定
- 缶を一方向へ回転
- 約1.2〜1.5回転撮影
- 4K程度の高解像度入力を想定

実際の撮影ではターンテーブルや専用ジグを使用する可能性があるが、その設計は本プロジェクトの対象外とする。

---

## 6. Fundamental Model

最終的に生成したい展開画像を

\[
I(u,v)
\]

とする。

- \(u\): 缶周方向
- \(v\): 缶高さ方向

缶表面の絶対角度を \(\theta\) とすると、

\[
u = \frac{\theta}{2\pi}W
\]

で展開画像の横座標へ対応させる。

各動画フレーム \(t\) の缶回転角を

\[
\phi_t
\]

とする。

フレーム内の横位置 \(x\) が円筒正面からの局所角度

\[
\alpha(x)
\]

に対応すると考える。

理想的な円筒・投影モデルでは、

\[
x = R_{\text{image}}\sin\alpha
\]

より、

\[
\alpha(x)=
\arcsin
\left(
\frac{x}{R_{\text{image}}}
\right)
\]

となる。

したがって、その画素が観測している缶表面角度は、

\[
\theta(x,t)=\phi_t+\alpha(x)
\]

と表現できる。

本プロジェクトでは問題を主に以下へ分離する。

1. フレーム回転角 \(\phi_t\) の推定
2. 円筒投影モデル \(\alpha(x)\)
3. 複数観測からの再構成
4. 回転軌跡のGlobal Optimization
5. 360° Loop Closure

---

## 7. Algorithms to Explore

### Motion / Rotation Estimation

最低限、以下を比較可能にする。

- Narrow-strip cross correlation
- Phase correlation
- Feature matching
- Sparse optical flow
- Dense optical flow

将来的な追加候補:

- ECC image alignment
- その他のregistration方式

---

## 8. Trajectory Estimation

以下を比較する。

### Sequential Integration

隣接フレーム推定値を積算する。

\[
\phi_t=
\sum_{k=0}^{t-1}\Delta_k
\]

### Global Optimization

複数フレーム間の観測

\[
\phi_j-\phi_i\approx d_{ij}
\]

を利用して、

\[
\min_{\phi}
\sum_{(i,j)}
\rho
\left(
(\phi_j-\phi_i)-d_{ij}
\right)
\]

を解く。

Huber lossなどのロバスト損失を利用できる構造とする。

### Loop Closure

1周後に同じラベル位置が再出現することを利用し、

\[
\phi_j-\phi_i=2\pi
\]

という制約をGlobal Optimizationへ追加する。

---

## 9. Reconstruction Algorithms

最低限、以下を比較する。

### Center Strip

各フレーム中央付近の細い縦ストリップのみを使用。

最重要baseline。

### Cylindrical Nearest

画像内の各画素を円筒座標へ逆投影し、その座標に最も近い観測を採用。

### Cylindrical Weighted Mean

同じ表面位置に対応する複数観測を重み付き平均。

例:

\[
w_{\text{angle}}=
\cos^n(\alpha)
\]

### Best Frame Selection

同一表面位置について最も品質の高い観測のみを採用。

### Robust Multi-frame Reconstruction

複数フレームを融合する。

将来的な品質指標候補:

- 正面度
- sharpness
- exposure
- temporal consistency
- specular highlight score

---

## 10. Synthetic Renderer

Prototype 0では実物動画より先にSynthetic Rendererを作成する。

目的:

> 完全なGround Truthが既知の状態で、座標系・円筒投影・再構成処理の正しさを検証する。

入力:

```text
flat_label.png
```

出力:

```text
frame_0000.png
frame_0001.png
...
frame_N.png
```

既知パラメータ:

- cylinder radius
- output frame width / height
- rotation angle per frame
- total rotation angle
- label dimensions
- camera geometry

初期版では以下を仮定する。

- 正射影に近い単純モデル
- カメラ位置固定
- 円筒軸固定
- 回転速度一定
- noiseなし
- blurなし
- lighting変動なし
- specular reflectionなし
- compressionなし

Synthetic Rendererには各フレームのGround Truth回転角

\[
\phi_t
\]

を必ず保存する。

---

## 11. Synthetic Degradation

基本pipelineが成立した後、Synthetic Rendererへ一つずつ劣化要因を追加する。

候補:

- Gaussian blur
- motion blur
- sensor noise
- JPEG compression
- exposure variation
- rotation speed variation
- horizontal drift
- vertical drift
- cylinder tilt
- camera tilt
- radius estimation error
- specular highlight
- partial occlusion

複数要因を最初から同時に入れない。

一つの変数だけを変化させ、失敗原因を特定可能にする。

---

## 12. Dataset Strategy

データセットは段階的に構築する。

## Dataset S — Sanity

1本。

処理しやすいラベル。

目的:

- pipeline成立確認
- 数式・座標系検証

## Dataset Q — Quality

3〜6種類程度。

可能なら以下の性質をカバーする。

- high texture
- low texture
- small text
- geometric pattern
- dark / low contrast
- reflective / metallic

## Dataset R — Robustness

スマートフォンアプリ化判断後に実施。

例:

- tilt
- uneven rotation
- fast rotation
- slow rotation
- lighting variation
- handheld
- off-center

---

## 13. Ground Truth

可能な缶については物理ラベルを剥がしてスキャンする。

想定:

```text
reference_scan_raw.png
reference_scan_aligned.png
```

`reference_scan_aligned.png` は比較用として、

- crop
- rotation
- scale
- perspective

程度の補正を許可する。

局所的なwarpなど、再構成アルゴリズムの誤差を隠す補正は禁止する。

Synthetic Datasetでは元のflat image自体を完全なGround Truthとする。

---

## 14. Evaluation

### Quantitative

候補:

- SSIM
- PSNR
- geometric alignment error
- edge displacement
- seam error
- sharpness
- OCR readability
- perceptual metric

数値指標は補助評価であり、単独で品質判定しない。

---

### Seam Evaluation

展開画像の左右端は本来連続するため、

```text
left edge ≈ right edge
```

であるべき。

色差、gradient、feature位置などからseam errorを評価する。

---

### Human Evaluation

最終評価ではアルゴリズム名を隠して比較する。

評価候補:

- 全体の自然さ
- 文字の読みやすさ
- 幾何学的歪み
- 継ぎ目
- ディテール
- 反射
- 実物ラベルらしさ

実物サイズへ印刷して比較することも重要な評価方法とする。

---

## 15. Technology Stack

### Language

Python 3.14を初期ターゲットとする。

`pyproject.toml`:

```toml
requires-python = ">=3.13,<3.15"
```

---

### Environment / Dependency Management

- uv
- pyproject.toml

基本操作例:

```bash
uv sync
uv run pytest
uv run canlabel ...
```

---

### Core Libraries

- NumPy
- OpenCV
- SciPy
- scikit-image

---

### Configuration

- PyYAML
- Python dataclasses

設定はYAMLからdataclassへ変換する。

内部コードでdictを直接参照し続ける設計は禁止する。

---

### CLI

Typerを使用。

想定:

```bash
uv run canlabel run experiments/baseline.yaml
uv run canlabel inspect dataset/beer001
uv run canlabel compare runs/run001 runs/run002
uv run canlabel report runs/run001
```

---

### Reporting

- Jinja2
- Matplotlib
- HTML/CSS

JavaScriptベースの複雑なUIは不要。

---

### Quality / Development Tools

- pytest
- ruff
- pyright または mypy

NumPy arrayのshapeまで高度な型システムで表現しない。

必要なshape・dtype・color formatはdocstringとruntime assertionで明示する。

---

## 16. Architecture

主要コンポーネントは交換可能にする。

```text
FrameSource
    ↓
Preprocessor
    ↓
MotionEstimator
    ↓
TrajectoryEstimator
    ↓
Projector
    ↓
Reconstructor
    ↓
Evaluator
    ↓
Reporter
```

アルゴリズム固有APIをpipeline外へ漏らさない。

例:

```python
class MotionEstimator(Protocol):
    def estimate(
        self,
        reference: np.ndarray,
        target: np.ndarray,
    ) -> MotionEstimate:
        ...
```

実装例:

```text
PhaseCorrelationEstimator
FeatureEstimator
OpticalFlowEstimator
```

設定だけで切り替え可能にする。

---

## 17. Frame Abstraction

最小限のメタデータラッパーを用意する。

例:

```python
@dataclass
class Frame:
    index: int
    timestamp: float
    image: np.ndarray
```

画像そのものの共通表現は `numpy.ndarray` とする。

---

## 18. FrameSource

動画・連続静止画を同じpipelineへ流せる構造にする。

```python
class FrameSource(Protocol):
    def __iter__(self) -> Iterator[Frame]:
        ...
```

初期実装:

```text
OpenCvVideoSource
ImageSequenceSource
```

将来的にFFmpegベースのreaderを追加可能にする。

---

## 19. Repository Structure

```text
can-label-lab/

  pyproject.toml
  uv.lock
  README.md

  src/
    canlabel/

      io/
        video.py
        images.py
        dataset.py

      synthetic/
        renderer.py
        degradation.py

      preprocess/
        crop.py
        stabilize.py
        color.py

      tracking/
        base.py
        cross_correlation.py
        phase_correlation.py
        features.py
        optical_flow.py

      trajectory/
        integrate.py
        optimize.py
        loop_closure.py

      geometry/
        cylinder.py
        calibration.py

      reconstruction/
        center_strip.py
        nearest.py
        weighted.py
        robust.py

      evaluation/
        alignment.py
        similarity.py
        sharpness.py
        seam.py

      reporting/
        html.py
        plots.py

      config.py
      models.py
      cli.py

  experiments/
    synthetic_baseline.yaml
    baseline_strip.yaml
    phase_cylindrical.yaml
    feature_cylindrical.yaml
    flow_cylindrical.yaml
    multiframe.yaml

  dataset/
    README.md
    .gitkeep

  runs/
    .gitkeep

  tests/
    unit/
    synthetic/
    regression/
```

---

## 20. Git Policy

実動画、大きなGround Truth画像、実験出力はGitへ登録しない。

例:

```gitignore
dataset/*
!dataset/README.md
!dataset/.gitkeep

runs/*
!runs/.gitkeep
```

Git管理対象:

- source code
- experiment configuration
- documentation
- small synthetic fixtures
- tests

---

## 21. Experiment Configuration

例:

```yaml
dataset: synthetic/basic

tracking:
  method: ground_truth

trajectory:
  method: ground_truth

projection:
  method: center_strip

reconstruction:
  method: center_strip

output:
  width: 4096
  save_debug_images: true
```

コードを書き換えずに実験条件を変更できること。

---

## 22. Run Output

各実験は独立したrun directoryを生成する。

```text
runs/
  20260816_001_synthetic_baseline/

    config.yaml
    metadata.json

    result.png
    reference.png
    difference.png

    metrics.json
    trajectory.csv
    frame_quality.csv

    report.html

    debug/
```

run directoryだけで、

> 何を実行し、どの結果になったか

を後から再確認可能にする。

---

## 23. HTML Report

最低限以下を表示する。

```text
Experiment
Configuration

Input / Synthetic Source

Reference
[image]

Reconstruction
[image]

Difference
[image]

Metrics
SSIM
PSNR
Seam Error
etc.

Trajectory
[plot]

Parameters
...
```

ブラウザで `report.html` を開くだけで結果を理解できるようにする。

---

## 24. Testing Strategy

### Unit Tests

数学処理は厳密にテストする。

例:

```text
x = 0
→ alpha = 0

x = +radius
→ alpha = +pi/2

x = -radius
→ alpha = -pi/2
```

---

### Synthetic Tests

完全Ground Truthを利用。

```text
flat image
    ↓
Synthetic Renderer
    ↓
frames
    ↓
Reconstruction
    ↓
flat image
```

元画像との誤差を評価する。

---

### Regression Tests

高品質結果を得た段階で、小さなGolden Datasetを固定する。

PNG完全一致は禁止する。

例:

```text
SSIM >= threshold
trajectory RMSE <= threshold
seam_error <= threshold
```

画質劣化をCIで検出できるようにする。

---

## 25. Development Principles

1. 実験可能性を最優先する。
2. 特定アルゴリズムへ密結合しない。
3. 一度に複数要因を変更しない。
4. 各実験条件を保存する。
5. 画像だけでなく診断データを保存する。
6. 数値評価と目視評価を分離する。
7. 高度な方法が単純方式より良いとは仮定しない。
8. 最終品質が改善しない複雑化は採用しない。
9. Notebookを主要実装場所にしない。
10. 実装ロジックはすべて `src/` 配下へ置く。

---

## 26. Milestone Plan

### Milestone 1 — Synthetic Round-trip Baseline

完全に既知の円筒モデルを使用し、

```text
flat label
    ↓
Synthetic Renderer
    ↓
synthetic frames
    ↓
known rotation angles
    ↓
center-strip reconstruction
    ↓
reconstructed flat label
```

を成立させる。

---

### Milestone 2 — Rotation Estimation

Ground Truthの回転角を再構成側から隠す。

以下を順次追加:

- cross correlation
- phase correlation
- feature matching
- optical flow

Ground Truth trajectoryとの誤差を比較する。

---

### Milestone 3 — Cylindrical Reconstruction

中央ストリップではなく、フレームの広い範囲を円筒座標へ逆投影する。

---

### Milestone 4 — Multi-frame Reconstruction

同一ラベル位置の複数観測を利用する。

比較:

- nearest
- weighted mean
- best frame
- robust blend

---

### Milestone 5 — Global Trajectory Optimization

複数フレーム間制約からtrajectoryを最適化する。

---

### Milestone 6 — Loop Closure

一周後の同一ラベル位置を検出し、360°制約を利用する。

---

### Milestone 7 — Synthetic Degradation

各種ノイズ・姿勢変動・反射等を個別に追加して耐性評価する。

---

### Milestone 8 — Real Can Dataset

ターンテーブル等で撮影した実缶動画を投入する。

Ground Truth scanと比較する。

---

## 27. Milestone 1 — Detailed Specification

### Objective

任意の平面ラベルPNGから円筒回転画像列を生成し、それを既知角度を用いたcenter-strip方式で展開画像へ戻す。

この段階ではmotion estimationを行わない。

---

### Input

例:

```text
tests/data/synthetic/label_basic.png
```

テスト用画像には以下を含める。

- アルファベット
- 数字
- 細い線
- 太い線
- 円
- checkerboard
- グラデーション
- 左右端を跨ぐ図形

左右端を跨ぐ要素はseam評価に利用する。

---

### Renderer Configuration

例:

```yaml
synthetic:
  source: tests/data/synthetic/label_basic.png

  frame:
    width: 1920
    height: 1080

  cylinder:
    radius_px: 300
    visible_height_px: 800

  rotation:
    start_deg: 0
    end_deg: 450
    frames: 450

  degradation:
    enabled: false
```

---

### Renderer Output

```text
synthetic_frames/
  frame_0000.png
  frame_0001.png
  ...
  frame_0449.png

trajectory.csv
metadata.json
```

`trajectory.csv`:

```csv
frame,angle_deg
0,0.0
1,1.0022
...
449,450.0
```

---

### Projection

初期モデルでは円筒の見かけの中心を既知とする。

中心からの横距離を \(x\)、見かけ半径を \(R\) として、

\[
\alpha=\arcsin(x/R)
\]

を使用する。

Milestone 1では高度なperspective camera modelは不要。

---

### Center Strip Reconstruction

既知の \(\phi_t\) を利用する。

各フレームについて、円筒中央付近から縦ストリップを取得する。

初期値例:

```yaml
reconstruction:
  method: center_strip
  strip_width_px: 4
```

各ストリップをGround Truth angleに基づいて展開座標へ配置する。

単純な「フレーム番号順に連結」ではなく、角度から出力座標を決定する。

---

### Output Resolution

出力横幅は設定可能にする。

例:

```yaml
output:
  width: 4096
```

高さは元ラベルのaspect ratioまたは設定値から決定する。

---

### Milestone 1 Metrics

最低限:

- SSIM
- PSNR
- seam error

追加可能なら:

- edge difference
- absolute difference image

---

### Milestone 1 Report

HTML reportには最低限、

- source flat label
- representative synthetic frame
- reconstructed label
- difference image
- SSIM
- PSNR
- seam error
- renderer parameters
- reconstruction parameters

を含める。

---

## 28. Milestone 1 Acceptance Criteria

Milestone 1は以下をすべて満たした時点で完了とする。

- `uv sync` で環境構築できる。
- `uv run pytest` が成功する。
- CLIからsynthetic experimentを実行できる。
- 任意の平面PNGからsynthetic framesを生成できる。
- 各frameのGround Truth angleが保存される。
- Ground Truth angleを利用してcenter-strip reconstructionできる。
- reconstructed imageが生成される。
- referenceとのdifference imageが生成される。
- SSIM等のmetricが生成される。
- HTML reportが生成される。
- run directoryに実験条件が保存される。
- 同一configから実験を再現できる。

---

## 29. Initial Codex Task

最初の作業ではMilestone 1以外を実装しないこと。

特に以下をまだ実装しない。

- phase correlation
- SIFT
- optical flow
- global optimization
- loop closure
- real video processing
- AI/ML
- super-resolution

最初の目的は、研究基盤と座標系が正しいことを確認することである。

実装順序:

```text
1. repository / pyproject setup
2. config model
3. CLI skeleton
4. synthetic test label
5. Synthetic Renderer
6. trajectory output
7. center-strip reconstructor
8. metrics
9. HTML report
10. automated tests
```

各段階でテスト可能な状態を維持する。

---

## 30. Codex Working Rules

Codexは以下のルールに従う。

- 一度にMilestoneを跨いで実装しない。
- 新しい依存追加には理由を明確にする。
- 大規模なframeworkを導入しない。
- 画像処理ロジックとCLIを分離する。
- configuration値をコードへハードコードしない。
- OpenCV固有型をmodule境界へ漏らさない。
- numpy.ndarrayを画像データの基本形式とする。
- debug outputを必要に応じて保存できる構造とする。
- deterministicにできる処理はdeterministicにする。
- random処理にはseedを指定可能にする。
- エラーを黙って補正しない。
- 数学的前提が破られた場合は明確に失敗させる。
- 変更後は必ずtestsを実行する。
- 画質に関わる変更ではmetricsのbefore/afterを確認する。

---

## 31. First Command Goal

Milestone 1完了時には、repository rootで以下のような操作だけで実験できる状態を目指す。

```bash
uv sync

uv run pytest

uv run canlabel run experiments/synthetic_baseline.yaml
```

結果:

```text
runs/<run-id>/
```

が生成され、その中の

```text
report.html
```

を開けば実験結果を確認できること。

---

## 32. Guiding Principle

このプロジェクトでは、

> **複雑な画像処理を作ること自体を目的にしない。**

目的は、

> **クラフトビール缶のラベルを、剥がした実物ラベルの代替として鑑賞したくなる品質で保存すること。**

単純なアルゴリズムがその目的を達成するなら、それを採用する。

複雑なアルゴリズムは、実際に鑑賞品質を改善する場合にのみ採用する。
