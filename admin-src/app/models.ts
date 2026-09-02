export interface CmsUser { id: number; username: string; name: string; }
export interface SessionResponse { authenticated: boolean; csrfToken?: string; user?: CmsUser; }
export interface ResourceMeta { key: string; label: string; plural: string; group: string; description: string; singleton?: boolean; count?: number; activeCount?: number; }
export interface CmsOption { value: string | number; label: string; }
export interface CmsField { name: string; label: string; type: string; required: boolean; readonly: boolean; help: string; accept?: string; options?: CmsOption[]; }
export interface CmsItem { id: number; display: string; fields: Record<string, any>; cells: Record<string, string>; preview?: string; previewType?: string; }
export interface ListField { name: string; label: string; }
export interface Pagination { page: number; pages: number; total: number; pageSize: number; }
export interface ResourceResponse { resource: ResourceMeta; schema: CmsField[]; listFields: ListField[]; items: CmsItem[]; pagination: Pagination; }
export interface DetailResponse { resource: ResourceMeta; schema: CmsField[]; item: CmsItem; }
export interface DashboardResponse { resources: ResourceMeta[]; summary: { pages: number; activePages: number; sections: number; media: number; newEnquiries: number; }; recentEnquiries: CmsItem[]; }
