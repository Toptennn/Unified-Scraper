import { useState, useMemo } from 'react';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import Layout from '../components/Layout';
import TweetTable from '../components/TweetTable';
import type { Tweet, Toast } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TwitterPage() {
  const [authId, setAuthId] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [mode, setMode] = useState<string>('timeline');
  const [screenName, setScreenName] = useState<string>('');
  const [query, setQuery] = useState<string>('');
  const [count, setCount] = useState<number>(50);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [error, setError] = useState<string>('');
  
  // Authentication challenge states
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authLoading, setAuthLoading] = useState<boolean>(false);
  const [challenge, setChallenge] = useState<any>(null);
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  
  // Filter states
  const [usernameFilter, setUsernameFilter] = useState<string>('');
  const [keywordFilter, setKeywordFilter] = useState<string>('');
  const [toast, setToast] = useState<Toast | null>(null);

  // Filtered tweets based on filters
  const filteredTweets = useMemo(() => {
    return tweets.filter(tweet => {
      const matchesUsername = !usernameFilter || 
        tweet.username.toLowerCase().includes(usernameFilter.toLowerCase());
      const matchesKeyword = !keywordFilter || 
        tweet.text.toLowerCase().includes(keywordFilter.toLowerCase());
      return matchesUsername && matchesKeyword;
    });
  }, [tweets, usernameFilter, keywordFilter]);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAuthentication = async () => {
    if (!authId || !password) {
      showToast('Please enter both Auth ID and Password', 'error');
      return;
    }

    setAuthLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/X/auth/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auth_id: authId, password }),
      });

      const data = await res.json();

      if (data.success) {
        setIsAuthenticated(true);
        setChallenge(null);
        showToast('Authentication successful!');
      } else if (data.challenge) {
        setChallenge(data.challenge);
        setSessionId(data.session_id);
        showToast('Verification required. Please check the challenge below.', 'error');
      } else {
        setError(data.message || 'Authentication failed');
        showToast(data.message || 'Authentication failed', 'error');
      }
    } catch (err) {
      console.error(err);
      setError('Authentication failed. Please try again.');
      showToast('Authentication failed. Please try again.', 'error');
    }

    setAuthLoading(false);
  };

  const handleVerification = async () => {
    if (!verificationCode) {
      showToast('Please enter the verification code', 'error');
      return;
    }

    setAuthLoading(true);

    try {
      const res = await fetch(`${API_URL}/X/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: sessionId, 
          response: verificationCode 
        }),
      });

      const data = await res.json();

      if (data.success) {
        setIsAuthenticated(true);
        setChallenge(null);
        setVerificationCode('');
        showToast('Verification successful!');
      } else if (data.challenge) {
        setChallenge(data.challenge);
        setVerificationCode('');
        showToast('Additional verification required', 'error');
      } else {
        setError(data.message || 'Verification failed');
        showToast(data.message || 'Verification failed', 'error');
      }
    } catch (err) {
      console.error(err);
      setError('Verification failed. Please try again.');
      showToast('Verification failed. Please try again.', 'error');
    }

    setAuthLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      showToast('Please authenticate first before scraping', 'error');
      return;
    }

    setLoading(true);
    setTweets([]);
    setError('');

    try {
      let endpoint = '';
      let body: any = {};
      
      if (mode === 'timeline') {
        endpoint = `${API_URL}/X/timeline/authenticated`;
        body = { 
          auth_id: authId, 
          screen_name: screenName, 
          count: parseInt(count.toString()) 
        };
      } else {
        endpoint = `${API_URL}/X/search/authenticated`;
        body = {
          auth_id: authId,
          query,
          count: parseInt(count.toString()),
          mode,
          start_date: startDate || null,
          end_date: endDate || null,
        };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      
      if (!res.ok) {
        if (res.status === 401) {
          setIsAuthenticated(false);
          throw new Error('Authentication expired. Please re-authenticate.');
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data: Tweet[] = await res.json();
      setTweets(data);
      showToast(`Successfully scraped ${data.length} tweets!`);
    } catch (err) {
      console.error(err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to scrape tweets. Please try again.';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    }

    setLoading(false);
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const exportToCSV = () => {
    const exportData = filteredTweets.map(tweet => ({
      post_date: formatDate(tweet.created_at),
      username: tweet.username,
      text: tweet.text,
      url: tweet.url || `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`,
      retweet_count: tweet.retweet_count || 0,
      favorite_count: tweet.favorite_count || 0,
      reply_count: tweet.reply_count || 0,
    }));

    const csv = Papa.unparse(exportData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tweets_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('CSV exported successfully!');
  };

  const exportToExcel = () => {
    const exportData = filteredTweets.map(tweet => ({
      post_date: formatDate(tweet.created_at),
      username: tweet.username,
      text: tweet.text,
      url: tweet.url || `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`,
      retweet_count: tweet.retweet_count || 0,
      favorite_count: tweet.favorite_count || 0,
      reply_count: tweet.reply_count || 0,
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Tweets');
    XLSX.writeFile(wb, `tweets_${new Date().toISOString().split('T')[0]}.xlsx`);
    showToast('Excel file exported successfully!');
  };

  return (
    <Layout 
      title="X (Twitter) Scraper - Advanced Data Extraction Tool"
      description="Comprehensive Twitter data extraction tool for timelines, searches, and user content with export capabilities"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              X (Twitter) Scraper
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Comprehensive Twitter data extraction tool for timelines, searches, and user content 
              with advanced filtering and export capabilities.
            </p>
          </div>

          {/* Toast Notifications */}
          {toast && (
            <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
              toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'
            } text-white`}>
              {toast.message}
            </div>
          )}

          {/* Scraping Form */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Twitter Data Extraction
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Authentication Section */}
              {!isAuthenticated ? (
                <div className="border-2 border-dashed border-orange-300 dark:border-orange-700 rounded-lg p-6 bg-orange-50 dark:bg-orange-900/20">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Step 1: Authentication Required
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="space-y-2">
                      <label htmlFor="auth-id" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Auth ID / Username
                      </label>
                      <input
                        id="auth-id"
                        type="text"
                        value={authId}
                        onChange={(e) => setAuthId(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        required
                        disabled={authLoading}
                      />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Password
                      </label>
                      <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        required
                        disabled={authLoading}
                      />
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleAuthentication}
                    disabled={authLoading}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-medium rounded-lg transition-colors duration-200"
                  >
                    {authLoading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Authenticating...
                      </>
                    ) : (
                      "Authenticate with Twitter"
                    )}
                  </button>

                  {/* Verification Challenge */}
                  {challenge && (
                    <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                      <h4 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                        Verification Required
                      </h4>
                      <p className="text-yellow-700 dark:text-yellow-300 mb-4 whitespace-pre-wrap">
                        {challenge.message}
                      </p>
                      {challenge.hint && (
                        <p className="text-sm text-yellow-600 dark:text-yellow-400 mb-4">
                          Hint: {challenge.hint}
                        </p>
                      )}
                      <div className="flex gap-4">
                        <input
                          type="text"
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value)}
                          placeholder={challenge.challenge_type === 'email_verification' ? 'Enter email address' : 'Enter confirmation code'}
                          className="flex-1 px-3 py-2 border border-yellow-300 dark:border-yellow-600 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          disabled={authLoading}
                        />
                        <button
                          type="button"
                          onClick={handleVerification}
                          disabled={authLoading || !verificationCode}
                          className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-400 text-white font-medium rounded-lg transition-colors"
                        >
                          {authLoading ? 'Verifying...' : 'Submit'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="border-2 border-dashed border-green-300 dark:border-green-700 rounded-lg p-4 bg-green-50 dark:bg-green-900/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-200">
                        ✅ Authenticated as: {authId}
                      </h3>
                      <p className="text-green-600 dark:text-green-400">
                        You can now proceed with scraping
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setIsAuthenticated(false);
                        setChallenge(null);
                        setVerificationCode('');
                        setSessionId('');
                      }}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              )}

              {/* Scraping Configuration (only show when authenticated) */}
              {isAuthenticated && (
                <>
                  {/* Mode Selection */}
                  <div className="space-y-2">
                    <label htmlFor="mode" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Scraping Mode
                    </label>
                    <select
                      id="mode"
                      value={mode}
                      onChange={(e) => setMode(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="timeline">User Timeline</option>
                      <option value="latest">Latest Tweets</option>
                      <option value="popular">Popular Tweets</option>
                    </select>
                  </div>

                  {/* Conditional Fields */}
                  {mode === 'timeline' ? (
                    <div className="space-y-2">
                      <label htmlFor="screen-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Screen Name (Username)
                      </label>
                      <input
                        id="screen-name"
                        type="text"
                        value={screenName}
                        onChange={(e) => setScreenName(e.target.value)}
                        placeholder="e.g., elonmusk"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        required
                      />
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Search Query
                        </label>
                        <input
                          id="search-query"
                          type="text"
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="Enter search terms..."
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          required
                        />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Start Date
                          </label>
                          <input
                            id="start-date"
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        <div className="space-y-2">
                          <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            End Date
                          </label>
                          <input
                            id="end-date"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <label htmlFor="tweet-count" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Number of Tweets
                    </label>
                    <input
                      id="tweet-count"
                      type="number"
                      value={count}
                      onChange={(e) => setCount(Number(e.target.value))}
                      min="1"
                      max="1000"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-medium rounded-lg transition-colors duration-200"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Scraping...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                        </svg>
                        Start Scraping
                      </>
                    )}
                  </button>
                </>
              )}
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}
          </div>

          {/* Filters */}
          {tweets.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Filter Results ({filteredTweets.length} of {tweets.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Filter by Username
                  </label>
                  <input
                    type="text"
                    value={usernameFilter}
                    onChange={(e) => setUsernameFilter(e.target.value)}
                    placeholder="Enter username to filter..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Filter by Keywords
                  </label>
                  <input
                    type="text"
                    value={keywordFilter}
                    onChange={(e) => setKeywordFilter(e.target.value)}
                    placeholder="Enter keywords to filter..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {tweets.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <TweetTable
                tweets={filteredTweets}
                onExportCSV={exportToCSV}
                onExportExcel={exportToExcel}
              />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
