export type WorkspaceKind = 'novel' | 'analysis';
export interface DocumentInfo {
  path: string;
  title: string;
  group: string;
  updatedAt: string;
  size: number;
  fingerprint: string;
  status?: string;
  approval?: string;
  protected?: boolean;
}
export interface Workspace {
  id: string;
  title: string;
  kind: WorkspaceKind;
  root: string;
  documents: DocumentInfo[];
  revision: string;
  updatedAt: string;
  warnings: string[];
  nextAction?: string;
  stage?: string;
  chineseFilenames: boolean;
}
export interface Catalog { workspaces: Workspace[]; warnings: string[]; roots: string[] }

export function documentUrl(id: string, relative: string): string {
  return `/workspaces/${id}/${relative.split('/').map(encodeURIComponent).join('/')}`;
}

export function referenceSelectionPath(chinese: boolean, chapter: number): string {
  const number = String(chapter).padStart(3, '0');
  return chinese ? `上下文/第${number}章-拆书参考.yaml` : `context-packages/chapter-${number}.references.yaml`;
}

export function referenceSelectionRequest(
  analysis: { root: string; registryFingerprint?: string },
  target: Pick<Workspace, 'root' | 'chineseFilenames'>,
  chapter: number,
  cardIds: string[],
): string {
  const selection = referenceSelectionPath(target.chineseFilenames, chapter);
  const fingerprint = analysis.registryFingerprint ? `，并复核清单指纹 ${analysis.registryFingerprint}` : '';
  return [
    `使用 $produce-long-form-novel，为小说 ${JSON.stringify(target.root)} 第 ${chapter} 章准备拆书参考。来源是 ${JSON.stringify(analysis.root)} 的 ${cardIds.join('、')}。`,
    `按 references/analysis-to-novel.md 核对证据与覆盖范围${fingerprint}，对照本书的计划与必要事实。`,
    `只对适用项写明本章用途、原创改造、保留距离和可检验效果，保存到 ${selection} 并运行 analysis_reference.py validate。全部不适用时直接说明原因。`,
    '本次到参考清单和校验结果为止。保留已有编辑，遇到冲突先说明。正文、审校和正式生产进度留待作者另行指定。',
  ].join('\n');
}

export function isChapterProse(relative: string): boolean {
  return /^(?:chapters\/chapter-\d+\/draft(?:-humanized)?|章节\/第\d+章\/正文(?:初稿|修订稿))\.md$/i.test(relative);
}

export function preferredChapters(documents: DocumentInfo[]): DocumentInfo[] {
  const chapters = new Map<string, DocumentInfo>();
  for (const document of documents) {
    if (!isChapterProse(document.path)) continue;
    const directory = document.path.slice(0, document.path.lastIndexOf('/'));
    if (!chapters.has(directory) || /\/(?:draft-humanized|正文修订稿)\.md$/i.test(document.path)) {
      chapters.set(directory, document);
    }
  }
  return [...chapters.values()];
}
