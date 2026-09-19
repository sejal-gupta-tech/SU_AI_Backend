import os

# Ensure directory exists
dir_path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\social-platforms\facebook'
os.makedirs(dir_path, exist_ok=True)

path = os.path.join(dir_path, 'page.tsx')

content = """"use client";

import { useState } from "react";
import { Loader2, Check, Facebook } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

export default function FacebookIntegrationPage() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [updated, setUpdated] = useState(false);
  
  const [fbPageId, setFbPageId] = useState("");
  const [fbToken, setFbToken] = useState("");

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await api.put('/api/v1/business', {
        fb_page_id: fbPageId,
        fb_access_token: fbToken
      });
      setUpdated(true);
      setTimeout(() => setUpdated(false), 3000);
    } catch (error) {
      console.error("Failed to update Facebook", error);
      alert("Failed to save settings");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center gap-2">
        <Facebook className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Facebook Integration</h1>
          <p className="text-muted-foreground mt-1">Connect your Facebook Page to automate publishing.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Facebook className="h-5 w-5 text-blue-600" />
            <CardTitle>Facebook API Settings</CardTitle>
          </div>
          <CardDescription>Enter your Facebook Graph API credentials below.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Facebook Page ID</Label>
            <Input 
              placeholder="e.g. 10435..." 
              value={fbPageId}
              onChange={(e) => setFbPageId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Page Access Token</Label>
            <Input 
              type="password" 
              placeholder="EAA..." 
              value={fbToken}
              onChange={(e) => setFbToken(e.target.value)}
            />
          </div>
          <Button onClick={handleUpdate} disabled={isUpdating} className="w-full bg-blue-600 hover:bg-blue-700">
            {isUpdating ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
            ) : updated ? (
              <><Check className="mr-2 h-4 w-4" /> Saved</>
            ) : (
              "Save Facebook Settings"
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
