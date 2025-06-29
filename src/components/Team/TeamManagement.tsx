import React, { useState, useEffect } from 'react';
import { Search, Plus, Mail, User, Edit2, Trash2, UserCheck, UserX } from 'lucide-react';
import { TeamMember } from '../../types';
import { emailApi } from '../../services/api';

interface OutlookContact {
  name: string;
  email: string;
  company: string;
  department: string;
  job_title: string;
  source: string;
}

export const TeamManagement: React.FC = () => {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<OutlookContact[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedContact, setSelectedContact] = useState<OutlookContact | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    try {
      setIsLoading(true);
      const response = await emailApi.getTeamMembers();
      setTeamMembers(response);
    } catch (error) {
      console.error('Error fetching team members:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchOutlookContacts = async () => {
    if (!searchTerm.trim()) return;
    
    try {
      setIsSearching(true);
      const response = await emailApi.searchContacts(searchTerm);
      setSearchResults(response.data.contacts || []);
    } catch (error) {
      console.error('Error searching contacts:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const addTeamMember = async (contact: OutlookContact, role: string) => {
    try {
      const memberData = {
        name: contact.name,
        email: contact.email,
        role: role || contact.job_title || 'Team Member',
        active: true
      };

      await emailApi.addTeamMember(memberData);
      await fetchTeamMembers();
      setShowAddForm(false);
      setSelectedContact(null);
      setSearchTerm('');
      setSearchResults([]);
    } catch (error) {
      console.error('Error adding team member:', error);
    }
  };

  const toggleMemberStatus = async (memberId: string, currentStatus: boolean) => {
    try {
      await emailApi.updateTeamMember(parseInt(memberId), { active: !currentStatus });
      await fetchTeamMembers();
    } catch (error) {
      console.error('Error updating team member:', error);
    }
  };

  const removeMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this team member?')) return;
    
    try {
      await emailApi.removeTeamMember(parseInt(memberId));
      await fetchTeamMembers();
    } catch (error) {
      console.error('Error removing team member:', error);
    }
  };

  return (
    <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Team Management</h2>
        <p className="text-neutral-600 dark:text-neutral-400">Manage team members and their communication settings</p>
      </div>

      {/* Search and Add Section */}
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-8 mb-8">
        <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">Add Team Members</h3>
        
        <div className="flex space-x-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-neutral-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchOutlookContacts()}
              placeholder="Search Outlook contacts by name or email..."
              className="w-full pl-10 pr-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
            />
          </div>
          <button
            onClick={searchOutlookContacts}
            disabled={!searchTerm.trim() || isSearching}
            className="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-lg font-medium text-neutral-900 dark:text-neutral-100">Search Results</h4>
            <div className="grid gap-3">
              {searchResults.map((contact, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl">
                  <div className="flex items-center space-x-4">
                    <div className="h-10 w-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">{contact.name}</p>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400">{contact.email}</p>
                      {contact.job_title && (
                        <p className="text-xs text-neutral-500 dark:text-neutral-500">{contact.job_title}</p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedContact(contact);
                      setShowAddForm(true);
                    }}
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-all duration-200 text-sm font-medium"
                  >
                    Add to Team
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Member Form Modal */}
      {showAddForm && selectedContact && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-surface-light dark:bg-card-dark rounded-2xl shadow-large dark:shadow-large-dark p-8 w-full max-w-md border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">Add Team Member</h3>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Name</label>
                <input
                  type="text"
                  value={selectedContact.name}
                  readOnly
                  className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Email</label>
                <input
                  type="email"
                  value={selectedContact.email}
                  readOnly
                  className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Role</label>
                <input
                  type="text"
                  defaultValue={selectedContact.job_title || 'Team Member'}
                  id="role-input"
                  className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                />
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setSelectedContact(null);
                }}
                className="flex-1 px-4 py-3 text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-xl transition-all duration-200 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const roleInput = document.getElementById('role-input') as HTMLInputElement;
                  addTeamMember(selectedContact, roleInput.value);
                }}
                className="flex-1 px-4 py-3 bg-primary-500 text-white hover:bg-primary-600 rounded-xl transition-all duration-200 font-medium"
              >
                Add Member
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Team Members List */}
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark">
        <div className="p-8 border-b border-neutral-200 dark:border-neutral-700">
          <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Current Team Members</h3>
          <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">{teamMembers.length} members</p>
        </div>

        <div className="p-8">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
              <p className="text-neutral-500 dark:text-neutral-400 mt-2">Loading team members...</p>
            </div>
          ) : teamMembers.length === 0 ? (
            <div className="text-center py-12">
              <User className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">No team members yet</h4>
              <p className="text-neutral-500 dark:text-neutral-400">Search and add team members from your Outlook contacts</p>
            </div>
          ) : (
            <div className="space-y-4">
              {teamMembers.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-6 bg-neutral-50 dark:bg-neutral-800/50 rounded-xl">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                      <User className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-3">
                        <h4 className="font-semibold text-neutral-900 dark:text-neutral-100">{member.name}</h4>
                        {member.active ? (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-lg">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 text-xs font-medium rounded-lg">
                            Inactive
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400">{member.email}</p>
                      <p className="text-sm text-neutral-500 dark:text-neutral-500">{member.role}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-xs text-neutral-500 dark:text-neutral-400">
                          Response Rate: {member.responseRate}%
                        </span>
                        {member.lastResponseAt && (
                          <span className="text-xs text-neutral-500 dark:text-neutral-400">
                            Last Response: {new Date(member.lastResponseAt).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleMemberStatus(member.id, member.active)}
                      className={`p-2 rounded-lg transition-all duration-200 ${
                        member.active
                          ? 'text-yellow-600 hover:bg-yellow-100 dark:hover:bg-yellow-900/30'
                          : 'text-green-600 hover:bg-green-100 dark:hover:bg-green-900/30'
                      }`}
                      title={member.active ? 'Deactivate member' : 'Activate member'}
                    >
                      {member.active ? <UserX className="h-5 w-5" /> : <UserCheck className="h-5 w-5" />}
                    </button>
                    <button
                      onClick={() => removeMember(member.id)}
                      className="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all duration-200"
                      title="Remove member"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};