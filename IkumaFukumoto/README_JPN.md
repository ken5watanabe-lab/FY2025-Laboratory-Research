# 福本育茉の成果

[🇺🇸 English](./README.md) | 🇯🇵 日本語  
このディレクトリは，2025年度医学研究実習（徳島大学 医学部 医学科 3年次科目）における福本育茉の研究ノート\*をまとめています．  
（\*公開可能なノート限定）  

## マウスの睡眠・覚醒状態を動画情報から分類する機械学習アルゴリズムの開発と評価

### 要旨

睡眠と運動機能の関係性を研究する場合, 活動性覚醒(AW), 静穏覚醒(QW), 非急速眼球運動(NREM)睡眠, 急速眼球運動(REM)睡眠の4状態システムにおける覚醒状態を分析することで, **行動分析の精度が向上する**. この脳4状態を評価するには, 脳波/筋電図 (EEG/EMG) 分析を行うための電極の埋め込みが必要である. この方法は正確だが, 侵襲的な手術とEEG/EMGデータのスコアリングをする専門家の育成という**高額な費用がかかる**[2]. 本研究では, 最新のコンピュータビジョン技術を活用し, 動画情報から睡眠と覚醒のサブステージを直接分類する方法論の開発を目指す. これにより, 手術や専門家によるスコアリングが不要になり, **マウスを用いた睡眠のハイスループット研究への道が開かれる**. 

![alt text](./images/fig1.png)

---

### 結果

重要な結果のみを示します.

![alt text](./images/fig2_mosaic.png)

![alt text](./images/fig3_mosaic.png)

![alt text](./images/fig4_mosaic.png)

## コードの利用

- 全ての解析および可視化のコードは[notebooks](./notebooks)及び[python/sleepens](./python/sleepens)に含まれています. 
- 動画データの共有にあたり使用した動画の変換コードは[python/h265encode](./python/h265encode)に含まれます。

## LICENSE

全てのライセンスは特に明示がない限り[リポジトリのライセンス](../LICENSE.md)に従います.

## Requirements

notebookの実行環境は今後公開される予定です。

SleepEnsの実行環境は[python/sleepens/.venv](./python/sleepens/.venv)に保存されています。

## 引用

[1] Fraigne, J. J. et al.  Sleep 2023.  
[2] Geuther, B. et al. Sleep 2022.


## 編集ログ

- Created this directory: Oct. 24, 2025 (Kengo Watanabe)
- Uploaded the notebooks, scripts: Oct. 27, 2025 (Ikuma Fukumoto)
- Edit README: Oct. 27, 2025 (Ikuma Fukumoto)
