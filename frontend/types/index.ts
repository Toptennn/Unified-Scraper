// DuckDuckGo Scraper Types
export interface SearchFormData {
  normal_query: string;
  exact_phrase: string;
  semantic_query: string;
  include_terms: string;
  exclude_terms: string;
  filetype: string;
  site_include: string;
  site_exclude: string;
  intitle: string;
  inurl: string;
  start_date: string;
  end_date: string;
  max_pages: number;
}

export interface SearchResult {
  title: string;
  url: string;
  description?: string;
  date?: string;
  post_date?: string;
  published_date?: string;
  [key: string]: any;
}

export interface SearchResponse {
  query: string;
  pages_retrieved: number;
  results: SearchResult[];
}

export interface SearchInfo {
  query: string;
  pages_retrieved: number;
  total_results: number;
}

export interface SearchFormProps {
  onSubmit: (data: SearchFormData) => void;
  loading: boolean;
}

export interface SearchResultsProps {
  results: SearchResult[];
  searchInfo: SearchInfo | null;
  loading: boolean;
  error: string | null;
}

// Twitter/X Scraper Types
export interface Tweet {
  tweet_id?: string;
  username: string;
  text: string;
  created_at: string;
  url?: string;
  retweet_count?: number;
  favorite_count?: number;
  reply_count?: number;
}

export interface Toast {
  message: string;
  type: 'success' | 'error';
}

export interface TwitterSearchParams {
  auth_id: string;
  auth_info_2: string;  // Email address
  password: string;
  screen_name?: string;
  query?: string;
  count: number;
  mode: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

export type SortDirection = 'asc' | 'desc';
export type SortField = keyof Tweet;

export interface FilterOptions {
  usernameFilter: string;
  keywordFilter: string;
}

export interface ExportData {
  post_date: string;
  username: string;
  text: string;
  url: string;
  retweet_count: number;
  favorite_count: number;
  reply_count: number;
}

// Common UI Types
export interface NavItem {
  name: string;
  href: string;
  current: boolean;
}
