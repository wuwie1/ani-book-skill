# 《遮天》阅读位置与校核方法

当前覆盖段可以从[覆盖地图](coverage-map.md)查到。[分批目录](batch-plan.md)按原文顺序列出起讫题、行号与各批审核。逐段笔记顶部有目录序号和原文位置，重号处尤其适合按行号定位。

原始文件与只读快照的指纹记录在[来源清单](source-manifest.md)。以原始换行、去除 UTF-8 BOM 后的 Unicode 偏移取区间，行号含首尾。末章以后的作者结束语和站点附文有独立目录单元。独立目录单元数、章题数和网页通行章数是不同统计口径。

全书复盘在[总评入口](book-analysis-review.md)，正在查看的批次也可以从这里返回。[状态文件](analysis-state.yaml)记录完成范围与审核入口。若需恢复，以[逐段坐标](source/segment-map.json)和实际存在的笔记比对；阶段结论回指针对该段的判断，底本错误保留在[文本说明](source-quality-review.md)。全文检索库可由本仓库 `scripts/analysis_retrieval.py build analyses/遮天` 重建。
