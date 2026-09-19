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
import { Library, Sparkles, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Loader2 } from 'lucide-react';
import { ContentPreview } from '@/components/content/ContentPreview';
import { Input } from '@/components/ui/input';

export default function ContentLibraryPage() {
  const [contents, setContents] = useState<GeneratedContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  const [selectedContent, setSelectedContent] = useState<GeneratedContent | null>(null);
  const [waPhone, setWaPhone] = useState("");
  const [isPublishingWa, setIsPublishingWa] = useState(false);

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

  const handlePublishWa = async () => {
    if (!selectedContent || !waPhone) return;
    setIsPublishingWa(true);
    try {
      await socialService.publishToWhatsApp(selectedContent._id, waPhone);
      alert("Successfully sent to WhatsApp!");
    } catch (error: any) {
      alert("Failed to publish: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsPublishingWa(false);
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
          <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-background rounded-xl shadow-xl relative animate-in fade-in zoom-in-95">
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
                
                <div className="p-6 border-t mt-4 bg-green-50/50">
                  <h3 className="font-semibold text-green-900 mb-2">Publish to WhatsApp Campaign</h3>
                  <p className="text-sm text-green-800 mb-4">Send this content directly to a target number using your WhatsApp Business API integration.</p>
                  <div className="flex gap-2 max-w-sm">
                    <Input 
                      placeholder="Target Phone Number (e.g. 919876543210)" 
                      value={waPhone} 
                      onChange={(e) => setWaPhone(e.target.value)} 
                    />
                    <Button onClick={handlePublishWa} disabled={isPublishingWa || !waPhone} className="bg-green-600 hover:bg-green-700">
                      {isPublishingWa ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4 mr-2" />}
                      Send
                    </Button>
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
