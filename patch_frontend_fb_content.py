import sys
import os

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\content-library\page.tsx'

content = """"use client";

import { useState, useEffect } from 'react';
import { contentService } from '@/services/content.service';
import { socialService } from '@/services/social.service';
import { GeneratedContent } from '@/types/content';
import { ContentCard } from '@/components/content/ContentCard';
import { ContentFilters } from '@/components/content/ContentFilters';
import { Library, Sparkles, Send, Instagram, Facebook } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Loader2 } from 'lucide-react';
import { ContentPreview } from '@/components/content/ContentPreview';
import { Input } from '@/components/ui/input';
import api from '@/services/api';
import { Label } from '@/components/ui/label';

export default function ContentLibraryPage() {
  const [contents, setContents] = useState<GeneratedContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  const [selectedContent, setSelectedContent] = useState<GeneratedContent | null>(null);
  
  // WhatsApp State
  const [waPhone, setWaPhone] = useState("");
  const [isPublishingWa, setIsPublishingWa] = useState(false);
  const [showWaRegister, setShowWaRegister] = useState(false);
  const [waRegPhoneId, setWaRegPhoneId] = useState("");
  const [waRegToken, setWaRegToken] = useState("");
  const [isRegisteringWa, setIsRegisteringWa] = useState(false);

  // Instagram State
  const [isPublishingIg, setIsPublishingIg] = useState(false);
  const [showIgRegister, setShowIgRegister] = useState(false);
  const [igRegAccountId, setIgRegAccountId] = useState("");
  const [igRegToken, setIgRegToken] = useState("");
  const [isRegisteringIg, setIsRegisteringIg] = useState(false);

  // Facebook State
  const [isPublishingFb, setIsPublishingFb] = useState(false);
  const [showFbRegister, setShowFbRegister] = useState(false);
  const [fbRegPageId, setFbRegPageId] = useState("");
  const [fbRegToken, setFbRegToken] = useState("");
  const [isRegisteringFb, setIsRegisteringFb] = useState(false);

  useEffect(() => {
    fetchContents();
  }, []);

  const fetchContents = async () => {
    setIsLoading(true);
    try {
      const res = await contentService.getContents();
      setContents(res.data);
    } catch (error) {
      console.error("Failed to load contents:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await contentService.deleteContent(id);
      setContents(contents.filter(c => c._id !== id));
      if (selectedContent?._id === id) setSelectedContent(null);
    } catch (error) {
      console.error("Failed to delete content:", error);
    }
  };

  const handleSave = async (editedContent: GeneratedContent) => {
    try {
      await contentService.updateContent(editedContent._id, editedContent);
      setContents(contents.map(c => c._id === editedContent._id ? editedContent : c));
      setSelectedContent(editedContent);
    } catch (error) {
      console.error("Failed to save content:", error);
    }
  };

  // WhatsApp Publishing Flow
  const handlePublishWa = async () => {
    if (!selectedContent || !waPhone) return;
    setIsPublishingWa(true);
    try {
      await socialService.publishToWhatsApp(selectedContent._id, waPhone);
      alert("Successfully sent to WhatsApp!");
      setShowWaRegister(false); // Hide just in case it was open
    } catch (error: any) {
      const msg = error.response?.data?.detail || error.message;
      if (msg.toLowerCase().includes("not connected")) {
        setShowWaRegister(true);
      } else {
        alert("Failed to publish: " + msg);
      }
    } finally {
      setIsPublishingWa(false);
    }
  };

  const handleWaRegisterAndPublish = async () => {
    setIsRegisteringWa(true);
    try {
      await api.put('/api/v1/business', {
        whatsapp_phone_id: waRegPhoneId,
        whatsapp_token: waRegToken
      });
      setShowWaRegister(false);
      // Automatically retry the publish!
      await handlePublishWa();
    } catch (error) {
      alert("Failed to register WhatsApp credentials");
    } finally {
      setIsRegisteringWa(false);
    }
  };
  
  // Instagram Publishing Flow
  const handlePublishIg = async () => {
    if (!selectedContent) return;
    setIsPublishingIg(true);
    try {
      await socialService.publishToInstagram(selectedContent._id);
      alert("Successfully published to Instagram Feed!");
      setShowIgRegister(false);
    } catch (error: any) {
      const msg = error.response?.data?.detail || error.message;
      if (msg.toLowerCase().includes("not connected")) {
        setShowIgRegister(true);
      } else {
        alert("Failed to publish: " + msg);
      }
    } finally {
      setIsPublishingIg(false);
    }
  };

  const handleIgRegisterAndPublish = async () => {
    setIsRegisteringIg(true);
    try {
      await api.put('/api/v1/business', {
        ig_account_id: igRegAccountId,
        ig_access_token: igRegToken
      });
      setShowIgRegister(false);
      // Automatically retry the publish!
      await handlePublishIg();
    } catch (error) {
      alert("Failed to register Instagram credentials");
    } finally {
      setIsRegisteringIg(false);
    }
  };

  // Facebook Publishing Flow
  const handlePublishFb = async () => {
    if (!selectedContent) return;
    setIsPublishingFb(true);
    try {
      await socialService.publishToFacebook(selectedContent._id);
      alert("Successfully published to Facebook Page!");
      setShowFbRegister(false);
    } catch (error: any) {
      const msg = error.response?.data?.detail || error.message;
      if (msg.toLowerCase().includes("not connected")) {
        setShowFbRegister(true);
      } else {
        alert("Failed to publish: " + msg);
      }
    } finally {
      setIsPublishingFb(false);
    }
  };

  const handleFbRegisterAndPublish = async () => {
    setIsRegisteringFb(true);
    try {
      await api.put('/api/v1/business', {
        fb_page_id: fbRegPageId,
        fb_access_token: fbRegToken
      });
      setShowFbRegister(false);
      // Automatically retry the publish!
      await handlePublishFb();
    } catch (error) {
      alert("Failed to register Facebook credentials");
    } finally {
      setIsRegisteringFb(false);
    }
  };

  const filteredContents = contents.filter(c => {
    if (filter === 'All') return true;
    if (filter === 'Drafts' || filter === 'Scheduled' || filter === 'Published') {
      return c.status === filter;
    }
    if (filter === 'Posts') return c.type?.includes('Post') || c.type?.includes('Caption');
    if (filter === 'Reels') return c.type?.includes('Reel');
    if (filter === 'Ads') return c.type?.includes('Ad');
    return true;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500 relative">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-2">
          <Library className="h-6 w-6 text-primary-600" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Content Library</h1>
            <p className="text-muted-foreground mt-1">Manage your generated AI content and publish them.</p>
          </div>
        </div>
        <Button asChild>
          <Link href="/content">
            <Sparkles className="h-4 w-4 mr-2" />
            Generate New
          </Link>
        </Button>
      </div>

      <div className="bg-card border border-border p-4 rounded-lg shadow-sm">
        <ContentFilters currentFilter={filter} onFilterChange={setFilter} />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : filteredContents.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 text-center text-muted-foreground border rounded-lg bg-muted/20 border-dashed">
          <Library className="h-12 w-12 text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-medium text-foreground">No content found</h3>
          <p className="max-w-sm mt-1 mb-4">You haven't generated any content that matches this filter yet.</p>
          <Button variant="outline" asChild>
            <Link href="/content">Generate Content</Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredContents.map(content => (
            <ContentCard 
              key={content._id} 
              content={content} 
              onView={(c) => setSelectedContent(c)}
              onEdit={(c) => setSelectedContent(c)}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {selectedContent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={(e) => {
          if (e.target === e.currentTarget) setSelectedContent(null);
        }}>
          <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-background rounded-xl shadow-xl relative animate-in fade-in zoom-in-95">
            <Button 
              variant="ghost" 
              className="absolute top-2 right-2 z-10 rounded-full w-8 h-8 p-0"
              onClick={() => setSelectedContent(null)}
            >
              o
            </Button>
            <div className="p-1 pt-8">
                <ContentPreview 
                  content={selectedContent} 
                  onRegenerate={() => {}} 
                  onSave={handleSave} 
                />
                
                <div className="grid md:grid-cols-3 gap-4 mt-4">
                  {/* WhatsApp Publish Section */}
                  <div className="p-4 border-t md:border-t-0 md:border-r bg-green-50/50">
                    <h3 className="font-semibold text-green-900 mb-2">WhatsApp</h3>
                    <p className="text-xs text-green-800 mb-4">Send directly to target number.</p>
                    
                    {!showWaRegister ? (
                      <div className="flex flex-col gap-2 w-full">
                        <Input 
                          placeholder="Phone Number" 
                          value={waPhone} 
                          onChange={(e) => setWaPhone(e.target.value)}
                          className="h-8 text-xs"
                        />
                        <Button onClick={handlePublishWa} disabled={isPublishingWa || !waPhone} className="bg-green-600 hover:bg-green-700 h-8 text-xs">
                          {isPublishingWa ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3 mr-2" />}
                          Send Message
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-green-200 shadow-sm animate-in fade-in">
                        <p className="text-xs font-medium text-red-600">Please register API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Phone Number ID</Label>
                          <Input value={waRegPhoneId} onChange={(e) => setWaRegPhoneId(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div>
                          <Label className="text-[10px]">Access Token</Label>
                          <Input type="password" value={waRegToken} onChange={(e) => setWaRegToken(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleWaRegisterAndPublish} disabled={isRegisteringWa} className="w-full h-7 text-[10px] bg-green-600 hover:bg-green-700 px-1">
                            {isRegisteringWa ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null} Save & Publish
                          </Button>
                          <Button variant="outline" onClick={() => setShowWaRegister(false)} className="h-7 text-[10px] px-2">Cancel</Button>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Instagram Publish Section */}
                  <div className="p-4 border-t md:border-t-0 md:border-r bg-pink-50/50">
                    <h3 className="font-semibold text-pink-900 mb-2">Instagram</h3>
                    <p className="text-xs text-pink-800 mb-4">Post directly to Feed or Reels.</p>
                    
                    {!showIgRegister ? (
                      <Button onClick={handlePublishIg} disabled={isPublishingIg} className="w-full bg-pink-600 hover:bg-pink-700 h-8 text-xs">
                        {isPublishingIg ? <Loader2 className="h-3 w-3 animate-spin" /> : <Instagram className="h-3 w-3 mr-2" />}
                        Publish Post
                      </Button>
                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-pink-200 shadow-sm animate-in fade-in">
                        <p className="text-xs font-medium text-red-600">Please register API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Instagram Account ID</Label>
                          <Input value={igRegAccountId} onChange={(e) => setIgRegAccountId(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div>
                          <Label className="text-[10px]">Access Token</Label>
                          <Input type="password" value={igRegToken} onChange={(e) => setIgRegToken(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleIgRegisterAndPublish} disabled={isRegisteringIg} className="w-full h-7 text-[10px] bg-pink-600 hover:bg-pink-700 px-1">
                            {isRegisteringIg ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null} Save & Publish
                          </Button>
                          <Button variant="outline" onClick={() => setShowIgRegister(false)} className="h-7 text-[10px] px-2">Cancel</Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Facebook Publish Section */}
                  <div className="p-4 border-t md:border-t-0 bg-blue-50/50">
                    <h3 className="font-semibold text-blue-900 mb-2">Facebook</h3>
                    <p className="text-xs text-blue-800 mb-4">Post directly to your Page.</p>
                    
                    {!showFbRegister ? (
                      <Button onClick={handlePublishFb} disabled={isPublishingFb} className="w-full bg-blue-600 hover:bg-blue-700 h-8 text-xs">
                        {isPublishingFb ? <Loader2 className="h-3 w-3 animate-spin" /> : <Facebook className="h-3 w-3 mr-2" />}
                        Publish Post
                      </Button>
                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-blue-200 shadow-sm animate-in fade-in">
                        <p className="text-xs font-medium text-red-600">Please register API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Facebook Page ID</Label>
                          <Input value={fbRegPageId} onChange={(e) => setFbRegPageId(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div>
                          <Label className="text-[10px]">Access Token</Label>
                          <Input type="password" value={fbRegToken} onChange={(e) => setFbRegToken(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleFbRegisterAndPublish} disabled={isRegisteringFb} className="w-full h-7 text-[10px] bg-blue-600 hover:bg-blue-700 px-1">
                            {isRegisteringFb ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null} Save & Publish
                          </Button>
                          <Button variant="outline" onClick={() => setShowFbRegister(false)} className="h-7 text-[10px] px-2">Cancel</Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
