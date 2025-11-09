/**
 * Search Page Component
 * Simple search functionality for posts by caption, location, or user
 */

import React, { useState } from 'react';
import { Search, Loader2, MapPin, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import PostCard from '@/components/ui/post-card';
import { useToast } from '@/hooks/use-toast';
import { apiService, Post } from '@/services/apiService';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!query.trim() || query.trim().length < 2) {
      toast({
        title: "Invalid Search",
        description: "Please enter at least 2 characters to search.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await apiService.searchPosts(query.trim());
      setResults(response.results);
      
      if (response.results.length === 0) {
        toast({
          title: "No Results",
          description: `No posts found for "${query}".`,
        });
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search posts. Please try again.');
      toast({
        title: "Search Failed",
        description: "Unable to search posts. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <ResponsiveLayout>
      <div className="max-w-4xl mx-auto">
        {/* Search Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-center mb-6">Search Posts</h1>
          
          {/* Search Bar */}
          <Card>
            <CardContent className="p-6">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search posts, locations, or users..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="pl-10"
                    disabled={isLoading}
                  />
                </div>
                <Button 
                  onClick={handleSearch}
                  disabled={isLoading || !query.trim()}
                  className="px-6"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Search
                    </>
                  )}
                </Button>
              </div>
              
              {/* Search Tips */}
              <div className="mt-4 text-sm text-muted-foreground">
                <p className="flex items-center gap-2">
                  <span>💡 Search in:</span>
                  <span className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    User names
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    Locations
                  </span>
                  <span>•</span>
                  <span>Post captions</span>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Error State */}
        {error && (
          <Alert className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Search Results */}
        {hasSearched && (
          <div>
            {/* Results Header */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold">
                {isLoading ? 'Searching...' : `Search Results${query ? ` for "${query}"` : ''}`}
              </h2>
              {!isLoading && results.length > 0 && (
                <p className="text-muted-foreground mt-1">
                  Found {results.length} {results.length === 1 ? 'post' : 'posts'}
                </p>
              )}
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin" />
                <span className="ml-2">Searching posts...</span>
              </div>
            )}

            {/* Results List */}
            {!isLoading && results.length > 0 && (
              <div className="space-y-6">
                {results.map((post) => (
                  <PostCard 
                    key={post.id} 
                    post={post}
                  />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!isLoading && hasSearched && results.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                  <Search className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Results Found</h3>
                <p className="text-muted-foreground mb-4">
                  No posts found for "{query}". Try different keywords.
                </p>
                <div className="text-sm text-muted-foreground">
                  <p>Try searching for:</p>
                  <ul className="mt-2 space-y-1">
                    <li>• Location names (e.g., "Paris", "Tokyo")</li>
                    <li>• User names or keywords in captions</li>
                    <li>• Travel-related terms</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!hasSearched && (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Search Posts</h3>
            <p className="text-muted-foreground">
              Enter keywords to search through posts, locations, and users.
            </p>
          </div>
        )}
      </div>
    </ResponsiveLayout>
  );
};

export default SearchPage;