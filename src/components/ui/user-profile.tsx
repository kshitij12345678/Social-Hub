import React, { useState } from 'react';
import { Edit2, MapPin, Calendar, Link as LinkIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { User } from '@/lib/mockData';

interface UserProfileProps {
  user: User;
  isOwnProfile?: boolean;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, isOwnProfile = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedUser, setEditedUser] = useState(user);

  const handleSave = () => {
    // In a real app, this would save to a backend
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedUser(user);
    setIsEditing(false);
  };

  return (
    <Card className="w-full shadow-card animate-fade-in">
      <CardHeader className="text-center pb-4">
        {/* Cover Image */}
        <div className="gradient-hero h-32 -mx-6 -mt-6 mb-6 rounded-t-lg relative">
          <div className="absolute inset-0 bg-black/10 rounded-t-lg"></div>
        </div>

        {/* Profile Picture */}
        <div className="relative -mt-20 mb-4">
          <div className="w-24 h-24 mx-auto rounded-full bg-card shadow-glow flex items-center justify-center text-4xl border-4 border-card">
            {user.avatar}
          </div>
        </div>

        {/* User Info */}
        <div className="space-y-2">
          {isEditing ? (
            <div className="space-y-3">
              <Input
                value={editedUser.name}
                onChange={(e) => setEditedUser({ ...editedUser, name: e.target.value })}
                className="text-center text-xl font-bold"
              />
              <Input
                value={editedUser.email}
                onChange={(e) => setEditedUser({ ...editedUser, email: e.target.value })}
                className="text-center text-muted-foreground"
              />
              <Textarea
                value={editedUser.bio}
                onChange={(e) => setEditedUser({ ...editedUser, bio: e.target.value })}
                className="text-center resize-none"
                rows={3}
              />
            </div>
          ) : (
            <>
              <h1 className="text-2xl font-bold text-foreground">{user.name}</h1>
              <p className="text-muted-foreground">{user.email}</p>
              <p className="text-foreground leading-relaxed">{user.bio}</p>
            </>
          )}
        </div>

        {/* Edit/Save Buttons */}
        {isOwnProfile && (
          <div className="flex justify-center space-x-2 mt-4">
            {isEditing ? (
              <>
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  Cancel
                </Button>
                <Button variant="default" size="sm" onClick={handleSave}>
                  Save Changes
                </Button>
              </>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="hover:bg-primary/10"
              >
                <Edit2 className="h-4 w-4 mr-2" />
                Edit Profile
              </Button>
            )}
          </div>
        )}

        {/* Follow Button for other profiles */}
        {!isOwnProfile && (
          <div className="flex justify-center mt-4">
            <Button variant="default" size="sm" className="transition-spring hover:scale-105">
              Follow
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent>
        <Separator className="mb-4" />
        
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="space-y-1">
            <p className="text-2xl font-bold text-foreground">{user.followers}</p>
            <p className="text-sm text-muted-foreground">Followers</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-foreground">{user.following}</p>
            <p className="text-sm text-muted-foreground">Following</p>
          </div>
        </div>

        <Separator className="my-4" />

        {/* Additional Info */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span className="text-sm">Joined January 2023</span>
          </div>
          <div className="flex items-center space-x-2 text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span className="text-sm">San Francisco, CA</span>
          </div>
          <div className="flex items-center space-x-2 text-muted-foreground">
            <LinkIcon className="h-4 w-4" />
            <span className="text-sm">portfolio.example.com</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default UserProfile;