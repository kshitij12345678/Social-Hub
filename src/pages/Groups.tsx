import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Plus, Users, Search, Trash2, UserPlus, ArrowLeft, MessageCircle, Edit, UserMinus, LogOut } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import { API_BASE_URL } from '@/config/api';

// Set the page title
document.title = 'Private Group - Social Hub';

interface User {
  id: number;
  full_name: string;
  email: string;
  profile_picture_url?: string;
}

interface GroupMember {
  id: number;
  group_id: number;
  user_id: number;
  joined_at: string;
  user: User;
  is_owner?: boolean;
}

interface Group {
  id: number;
  name: string;
  description?: string;
  created_by: number;
  created_at: string;
  members: User[];
  member_count: number;
}

const Groups: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showAddMemberDialog, setShowAddMemberDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showManageMembersDialog, setShowManageMembersDialog] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [groupMembers, setGroupMembers] = useState<GroupMember[]>([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [newGroup, setNewGroup] = useState({ name: '', description: '', member_emails: [] as string[] });
  const [createDialogSearchQuery, setCreateDialogSearchQuery] = useState('');
  const [createDialogSearchResults, setCreateDialogSearchResults] = useState<User[]>([]);
  const [editGroup, setEditGroup] = useState({ name: '', description: '' });
  const { toast } = useToast();
  const navigate = useNavigate();
  const { user } = useAuth();

  // Load groups on component mount
  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setGroups(data);
      } else {
        toast({
          title: "Error",
          description: "Failed to load groups",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      toast({
        title: "Error",
        description: "Failed to load groups",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createGroup = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newGroup.name,
          description: newGroup.description,
          member_emails: newGroup.member_emails.length > 0 ? newGroup.member_emails : undefined
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGroups([data, ...groups]);
        setNewGroup({ name: '', description: '', member_emails: [] });
        setCreateDialogSearchQuery('');
        setCreateDialogSearchResults([]);
        setShowCreateDialog(false);
        toast({
          title: "Success",
          description: `Group created successfully with ${data.member_count} members`,
        });
        
        // Navigate to Messages page with the newly created group
        navigate('/messages', { 
          state: { 
            openGroup: {
              id: data.id,
              name: data.name,
              rocket_chat_group_id: data.rocket_chat_group_id || `group-${data.id}`,
              type: 'private_group'
            }
          } 
        });
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to create group",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error creating group:', error);
      toast({
        title: "Error",
        description: "Failed to create group",
        variant: "destructive",
      });
    }
  };

  const searchUsers = async (query: string) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/users/search?query=${encodeURIComponent(query)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
      }
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  const searchUsersForCreateDialog = async (query: string) => {
    if (query.length < 2) {
      setCreateDialogSearchResults([]);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/users/search?query=${encodeURIComponent(query)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCreateDialogSearchResults(data);
      }
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  const addMemberToCreateGroup = (user: User) => {
    if (!newGroup.member_emails.includes(user.email)) {
      setNewGroup({
        ...newGroup,
        member_emails: [...newGroup.member_emails, user.email]
      });
      toast({
        title: "Success",
        description: `${user.full_name} added to group`,
      });
    } else {
      toast({
        title: "Info",
        description: `${user.full_name} is already added to group`,
      });
    }
  };

  const removeMemberFromCreateGroup = (email: string) => {
    setNewGroup({
      ...newGroup,
      member_emails: newGroup.member_emails.filter(e => e !== email)
    });
  };

  const addMemberToGroup = async (userEmail: string) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${selectedGroup.id}/members`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_email: userEmail }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Member added successfully",
        });
        loadGroups(); // Reload groups to update member count
        setShowAddMemberDialog(false);
        setSearchQuery('');
        setSearchResults([]);
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to add member",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error adding member:', error);
      toast({
        title: "Error",
        description: "Failed to add member",
        variant: "destructive",
      });
    }
  };

  const deleteGroup = async (groupId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${groupId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Group deleted successfully",
        });
        setGroups(groups.filter(g => g.id !== groupId));
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to delete group",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error deleting group:', error);
      toast({
        title: "Error",
        description: "Failed to delete group",
        variant: "destructive",
      });
    }
  };

  const leaveGroup = async (groupId: number) => {
    if (!user) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${groupId}/members/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "You have left the group",
        });
        setGroups(groups.filter(g => g.id !== groupId));
        setSelectedGroup(null);
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to leave group",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error leaving group:', error);
      toast({
        title: "Error",
        description: "Failed to leave group",
        variant: "destructive",
      });
    }
  };

  const updateGroup = async () => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${selectedGroup.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editGroup),
      });

      if (response.ok) {
        const updatedGroup = await response.json();
        setGroups(groups.map(g => g.id === selectedGroup.id ? updatedGroup : g));
        setShowEditDialog(false);
        setEditGroup({ name: '', description: '' });
        toast({
          title: "Success",
          description: "Group updated successfully",
        });
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to update group",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error updating group:', error);
      toast({
        title: "Error",
        description: "Failed to update group",
        variant: "destructive",
      });
    }
  };

  const openGroupChat = (group: any) => {
    // Navigate to Messages page with the group selected
    navigate('/messages', { 
      state: { 
        openGroup: {
          id: group.id,
          name: group.name,
          rocket_chat_group_id: group.rocket_chat_group_id || `group-${group.id}`,
          type: 'private_group'
        }
      } 
    });
  };

  const loadGroupMembers = async (groupId: number) => {
    setLoadingMembers(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${groupId}/members`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setGroupMembers(data);
      } else {
        toast({
          title: "Error",
          description: "Failed to load group members",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading group members:', error);
      toast({
        title: "Error",
        description: "Failed to load group members",
        variant: "destructive",
      });
    } finally {
      setLoadingMembers(false);
    }
  };

  const removeMemberFromGroup = async (memberId: number) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${selectedGroup.id}/members/${memberId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Member removed successfully",
        });
        // Reload members list
        loadGroupMembers(selectedGroup.id);
        // Reload groups to update member count
        loadGroups();
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to remove member",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error removing member:', error);
      toast({
        title: "Error",
        description: "Failed to remove member",
        variant: "destructive",
      });
    }
  };

  const setMemberAsOwner = async (memberId: number, memberUserId: number) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${selectedGroup.id}/members/${memberId}/set-owner`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Set owner response:', result);
        
        // Update the member in state immediately
        const updatedMembers = groupMembers.map((member) =>
          member.id === memberId ? { ...member, is_owner: true } : member
        );
        setGroupMembers(updatedMembers);
        
        toast({
          title: "Success",
          description: "Member promoted to owner successfully",
        });
        
        // Reload groups to sync up-to-date data
        loadGroups();
      } else {
        const error = await response.json();
        console.error('❌ Set owner error:', error);
        toast({
          title: "Error",
          description: error.detail || "Failed to set member as owner",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error setting member as owner:', error);
      toast({
        title: "Error",
        description: "Failed to set member as owner",
        variant: "destructive",
      });
    }
  };

  const removeMemberAsOwner = async (memberId: number, memberUserId: number) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/groups/${selectedGroup.id}/members/${memberId}/remove-owner`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Remove owner response:', result);
        
        // Update the member in state immediately
        const updatedMembers = groupMembers.map((member) =>
          member.id === memberId ? { ...member, is_owner: false } : member
        );
        setGroupMembers(updatedMembers);
        
        toast({
          title: "Success",
          description: "Member removed from owner status successfully",
        });
        
        // Reload groups to sync up-to-date data
        loadGroups();
      } else {
        const error = await response.json();
        console.error('❌ Remove owner error:', error);
        toast({
          title: "Error",
          description: error.detail || "Failed to remove member from owner status",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error removing member from owner:', error);
      toast({
        title: "Error",
        description: "Failed to remove member from owner status",
        variant: "destructive",
      });
    }
  };


  if (loading) {
    return (
      <ResponsiveLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading groups...</div>
        </div>
      </ResponsiveLayout>
    );
  }

  return (
    <ResponsiveLayout>
      <div className="w-full">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Private Groups</h1>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Group
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Private Group</DialogTitle>
              <DialogDescription>
                Create a new private group to collaborate with selected members.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="group-name">Group Name</Label>
                <Input
                  id="group-name"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                  placeholder="Enter group name"
                />
              </div>
              <div>
                <Label htmlFor="group-description">Description (Optional)</Label>
                <Textarea
                  id="group-description"
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                  placeholder="Enter group description"
                />
              </div>

              <div className="border-t pt-4">
                <Label htmlFor="search-create-users">Add Members (Optional)</Label>
                <div className="relative mt-2">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search-create-users"
                    placeholder="Search by name or email..."
                    value={createDialogSearchQuery}
                    onChange={(e) => {
                      setCreateDialogSearchQuery(e.target.value);
                      searchUsersForCreateDialog(e.target.value);
                    }}
                    className="pl-10"
                  />
                </div>

                {/* Selected Members Display */}
                {newGroup.member_emails.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-sm font-medium">Selected Members ({newGroup.member_emails.length})</p>
                    <div className="flex flex-wrap gap-2">
                      {newGroup.member_emails.map((email) => (
                        <Badge key={email} variant="secondary" className="flex items-center gap-1">
                          {email.split('@')[0]}
                          <button
                            onClick={() => removeMemberFromCreateGroup(email)}
                            className="ml-1 hover:text-destructive"
                          >
                            ✕
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Search Results */}
                {createDialogSearchResults.length > 0 && (
                  <div className="space-y-2 max-h-48 overflow-y-auto mt-3">
                    {createDialogSearchResults.map((user) => (
                      <div
                        key={user.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                      >
                        <div className="flex items-center space-x-3">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src={user.profile_picture_url} />
                            <AvatarFallback>
                              {user.full_name.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{user.full_name}</p>
                            <p className="text-sm text-muted-foreground">{user.email}</p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => addMemberToCreateGroup(user)}
                          disabled={newGroup.member_emails.includes(user.email)}
                        >
                          {newGroup.member_emails.includes(user.email) ? 'Added' : 'Add'}
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowCreateDialog(false);
                  setNewGroup({ name: '', description: '', member_emails: [] });
                  setCreateDialogSearchQuery('');
                  setCreateDialogSearchResults([]);
                }}
              >
                Cancel
              </Button>
              <Button onClick={createGroup} disabled={!newGroup.name.trim()}>
                Create Group
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {groups.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No groups yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first group to start collaborating with others.
            </p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Group
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {groups.map((group) => (
            <Card key={group.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{group.name}</CardTitle>
                    {group.description && (
                      <CardDescription className="mt-1">
                        {group.description}
                      </CardDescription>
                    )}
                  </div>
                  <Badge variant="secondary">
                    <Users className="w-3 h-3 mr-1" />
                    {group.member_count}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {group.members.slice(0, 3).map((member) => (
                      <div key={member.id} className="flex items-center space-x-2">
                        <Avatar className="w-6 h-6">
                          <AvatarImage src={member.profile_picture_url} />
                          <AvatarFallback>
                            {member.full_name.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-sm text-muted-foreground">
                          {member.full_name}
                        </span>
                      </div>
                    ))}
                    {group.member_count > 3 && (
                      <span className="text-sm text-muted-foreground">
                        +{group.member_count - 3} more
                      </span>
                    )}
                  </div>
                  
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      size="sm"
                      onClick={() => openGroupChat(group)}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      <MessageCircle className="w-4 h-4 mr-1" />
                      Chat
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedGroup(group);
                        setEditGroup({ name: group.name, description: group.description || '' });
                        setShowEditDialog(true);
                      }}
                    >
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedGroup(group);
                        setShowAddMemberDialog(true);
                      }}
                    >
                      <UserPlus className="w-4 h-4 mr-1" />
                      Add Member
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedGroup(group);
                        loadGroupMembers(group.id);
                        setShowManageMembersDialog(true);
                      }}
                    >
                      <Users className="w-4 h-4 mr-1" />
                      Manage Members
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteGroup(group.id)}
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </Button>
                    {group.created_by !== parseInt(user?.id || '0') && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => leaveGroup(group.id)}
                        className="text-red-600 border-red-600 hover:bg-red-50"
                      >
                        <LogOut className="w-4 h-4 mr-1" />
                        Leave
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Member Dialog */}
      <Dialog open={showAddMemberDialog} onOpenChange={setShowAddMemberDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Member to {selectedGroup?.name}</DialogTitle>
            <DialogDescription>
              Search for users to add to this group.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="search-users">Search Users</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search-users"
                  placeholder="Search by name or email..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    searchUsers(e.target.value);
                  }}
                  className="pl-10"
                />
              </div>
            </div>
            
            {searchResults.length > 0 && (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {searchResults.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex items-center space-x-3">
                      <Avatar className="w-8 h-8">
                        <AvatarImage src={user.profile_picture_url} />
                        <AvatarFallback>
                          {user.full_name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{user.full_name}</p>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => addMemberToGroup(user.email)}
                    >
                      Add
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddMemberDialog(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Group Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Group</DialogTitle>
            <DialogDescription>
              Update the group name and description.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-group-name">Group Name</Label>
              <Input
                id="edit-group-name"
                value={editGroup.name}
                onChange={(e) => setEditGroup({ ...editGroup, name: e.target.value })}
                placeholder="Enter group name"
              />
            </div>
            <div>
              <Label htmlFor="edit-group-description">Description (Optional)</Label>
              <Textarea
                id="edit-group-description"
                value={editGroup.description}
                onChange={(e) => setEditGroup({ ...editGroup, description: e.target.value })}
                placeholder="Enter group description"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={updateGroup} disabled={!editGroup.name.trim()}>
              Update Group
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Manage Members Dialog */}
      <Dialog open={showManageMembersDialog} onOpenChange={setShowManageMembersDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Manage Members - {selectedGroup?.name}</DialogTitle>
            <DialogDescription>
              View and remove members from this group.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {loadingMembers ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-muted-foreground">Loading members...</div>
              </div>
            ) : groupMembers.length === 0 ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-muted-foreground">No members in this group</div>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {groupMembers.map((member) => (
                  <div
                    key={member.id}
                    className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <Avatar className="w-10 h-10 flex-shrink-0">
                        <AvatarImage src={member.user.profile_picture_url} />
                        <AvatarFallback>
                          {member.user.full_name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium truncate">{member.user.full_name}</p>
                        <p className="text-sm text-muted-foreground truncate">{member.user.email}</p>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2 justify-end">
                      {selectedGroup?.created_by === member.user_id && (
                        <Badge variant="secondary" className="bg-green-100 text-green-800 flex-shrink-0">Creator</Badge>
                      )}
                      {member.is_owner && selectedGroup?.created_by !== member.user_id && (
                        <Badge variant="secondary" className="bg-blue-100 text-blue-800 flex-shrink-0">Owner</Badge>
                      )}
                      {selectedGroup?.created_by === member.user_id ? (
                        // Creator - no actions
                        <div />
                      ) : member.is_owner ? (
                        // Owner - show remove owner button and remove button
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => removeMemberAsOwner(member.id, member.user_id)}
                            className="text-orange-600 border-orange-600 hover:bg-orange-50 flex-shrink-0"
                          >
                            Remove from Owner
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => removeMemberFromGroup(member.user_id)}
                            className="flex-shrink-0"
                          >
                            <UserMinus className="w-4 h-4 mr-1" />
                            Remove
                          </Button>
                        </div>
                      ) : (
                        // Regular member - show Set Owner and Remove buttons
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setMemberAsOwner(member.id, member.user_id)}
                            className="text-blue-600 border-blue-600 hover:bg-blue-50 flex-shrink-0"
                          >
                            Set Owner
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => removeMemberFromGroup(member.user_id)}
                            className="flex-shrink-0"
                          >
                            <UserMinus className="w-4 h-4 mr-1" />
                            Remove
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowManageMembersDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </ResponsiveLayout>
  );
};

export default Groups;
