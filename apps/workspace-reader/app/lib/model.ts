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
