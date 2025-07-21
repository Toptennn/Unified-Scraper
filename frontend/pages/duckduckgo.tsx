import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import SearchForm from '../components/SearchForm';
import SearchResults from '../components/SearchResults';
import { SearchFormData, SearchResponse, SearchResult, SearchInfo } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

const DuckDuckGoPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchInfo, setSearchInfo] = useState<SearchInfo | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const eventSourceRef = useRef<EventSource | null>(null);

  const handleSearch = async (formData: SearchFormData): Promise<void> => {
    setLoading(true);
    setError(null);
    setResults([]);
    setSearchInfo(null);
    setProgress(0);

    const params = new URLSearchParams(formData as any).toString();
    const es = new EventSource(`${API_URL}/ddg/search-stream?${params}`);
    eventSourceRef.current = es;

    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'progress') {
        const pct = (data.current / data.total) * 100;
        setProgress(pct);
      } else if (data.type === 'complete') {
        setResults(data.results);
        setSearchInfo({
          query: data.query,
          pages_retrieved: data.pages_retrieved,
          total_results: data.results.length
        });
        setLoading(false);
        es.close();
      }
    };

    es.onerror = () => {
      setError('An error occurred while searching');
      setLoading(false);
      es.close();
    };
  };

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  return (
    <Layout 
      title="DuckDuckGo Scraper - Advanced Search Tool"
      description="Advanced DuckDuckGo search tool with powerful filtering options"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              DuckDuckGo Scraper
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Perform advanced searches on DuckDuckGo with semantic search, date filtering, 
              file type restrictions, and site-specific searches.
            </p>
          </div>

          <SearchForm onSubmit={handleSearch} loading={loading} />
          
          <SearchResults
            results={results}
            searchInfo={searchInfo}
            loading={loading}
            error={error}
            progress={progress}
          />
        </div>
      </div>
    </Layout>
  );
};

export default DuckDuckGoPage;
