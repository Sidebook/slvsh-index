export interface Trick {
  components: string[];
  start: number;
  end: number;
  title: string;
  video_id: string;
  url: string;
  upload_date: string;
}

export interface SearchResponse {
  results: Trick[];
  page: number;
  page_size: number;
  max_page: number;
  count: number;
}
