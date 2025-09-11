import React, { useState } from 'react';
import { Grid, List } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import UserProfile from '@/components/ui/user-profile';
import FeedPostCard from '@/components/ui/feed-post-card';
import { currentUser, mockPosts } from '@/lib/mockData';

const Profile = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  
  // Filter posts by current user
  const userPosts = mockPosts.filter(post => post.userId === currentUser.id);

  return (
    <ResponsiveLayout>
      <div className="max-w-4xl mx-auto">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Profile Info */}
          <div className="lg:col-span-1">
            <UserProfile user={currentUser} isOwnProfile={true} />
          </div>

          {/* Posts Section */}
          <div className="lg:col-span-2">
            <Card className="shadow-card animate-fade-in">
              <CardContent className="p-0">
                <Tabs defaultValue="posts" className="w-full">
                  <div className="border-b p-4">
                    <div className="flex items-center justify-between">
                      <TabsList className="grid w-full grid-cols-3 max-w-md">
                        <TabsTrigger value="posts">Posts</TabsTrigger>
                        <TabsTrigger value="photos">Photos</TabsTrigger>
                        <TabsTrigger value="videos">Videos</TabsTrigger>
                      </TabsList>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={viewMode === 'grid' ? 'default' : 'ghost'}
                          size="sm"
                          onClick={() => setViewMode('grid')}
                          className="hover:bg-primary/10"
                        >
                          <Grid className="h-4 w-4" />
                        </Button>
                        <Button
                          variant={viewMode === 'list' ? 'default' : 'ghost'}
                          size="sm"
                          onClick={() => setViewMode('list')}
                          className="hover:bg-primary/10"
                        >
                          <List className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <TabsContent value="posts" className="p-4">
                    {viewMode === 'list' ? (
                      <div className="space-y-6">
                        {userPosts.length > 0 ? (
                          userPosts.map((post) => (
                            <FeedPostCard key={post.id} post={post} />
                          ))
                        ) : (
                          <div className="text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Grid className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No posts yet</h3>
                            <p className="text-muted-foreground">Share your first post to get started!</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {userPosts.length > 0 ? (
                          userPosts.map((post) => (
                            <Card key={post.id} className="hover:shadow-soft transition-smooth animate-scale-in">
                              <CardContent className="p-4">
                                <div className="aspect-square bg-muted rounded-lg mb-3 flex items-center justify-center">
                                  <span className="text-4xl">📝</span>
                                </div>
                                <p className="text-sm text-foreground line-clamp-2 mb-2">
                                  {post.content}
                                </p>
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                  <span>{post.timestamp}</span>
                                  <span>{post.likes} likes</span>
                                </div>
                              </CardContent>
                            </Card>
                          ))
                        ) : (
                          <div className="col-span-full text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Grid className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No posts yet</h3>
                            <p className="text-muted-foreground">Share your first post to get started!</p>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="photos" className="p-4">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {[1, 2, 3, 4, 5, 6].map((i) => (
                        <Card key={i} className="aspect-square hover:shadow-soft transition-smooth animate-scale-in">
                          <CardContent className="p-0 h-full">
                            <div className="w-full h-full bg-muted rounded-lg flex items-center justify-center">
                              <span className="text-2xl">📸</span>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="videos" className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[1, 2, 3, 4].map((i) => (
                        <Card key={i} className="aspect-video hover:shadow-soft transition-smooth animate-scale-in">
                          <CardContent className="p-0 h-full">
                            <div className="w-full h-full bg-muted rounded-lg flex items-center justify-center">
                              <span className="text-3xl">🎥</span>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ResponsiveLayout>
  );
};

export default Profile;