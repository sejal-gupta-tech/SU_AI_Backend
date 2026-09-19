import os

dir_path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\social-platforms\linkedin'
os.makedirs(dir_path, exist_ok=True)

path = os.path.join(dir_path, 'page.tsx')

content = """"use client";

import { useState } from "react";
import { Loader2, Check, Linkedin } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

export default function LinkedinIntegrationPage() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [updated, setUpdated] = useState(false);
  
  const [authorId, setAuthorId] = useState("");
  const [token, setToken] = useState("");

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await api.put('/api/v1/business', {
        linkedin_author_id: authorId,
        linkedin_access_token: token
      });
      setUpdated(true);
      setTimeout(() => setUpdated(false), 3000);
    } catch (error) {
      console.error("Failed to update LinkedIn", error);
      alert("Failed to save settings");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center gap-2">
        <Linkedin className="h-8 w-8 text-blue-700" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">LinkedIn Integration</h1>
          <p className="text-muted-foreground mt-1">Connect your LinkedIn Profile or Company Page to automate publishing.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Linkedin className="h-5 w-5 text-blue-700" />
            <CardTitle>LinkedIn API Settings</CardTitle>
          </div>
          <CardDescription>Enter your LinkedIn API credentials below.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>LinkedIn Author ID</Label>
            <Input 
              placeholder="e.g. urn:li:person:12345..." 
              value={authorId}
              onChange={(e) => setAuthorId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Access Token</Label>
            <Input 
              type="password" 
              placeholder="AQV..." 
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
          </div>
          <Button onClick={handleUpdate} disabled={isUpdating} className="w-full bg-blue-700 hover:bg-blue-800">
            {isUpdating ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
            ) : updated ? (
              <><Check className="mr-2 h-4 w-4" /> Saved</>
            ) : (
              "Save LinkedIn Settings"
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
