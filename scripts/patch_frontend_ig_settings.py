import sys
import os

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\whatsapp\page.tsx'

content = """"use client";

import { useState } from "react";
import { Loader2, Check, Smartphone, Instagram } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

export default function IntegrationsPage() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [updated, setUpdated] = useState(false);
  
  // WhatsApp
  const [waPhoneId, setWaPhoneId] = useState("");
  const [waToken, setWaToken] = useState("");
  
  // Instagram
  const [igAccountId, setIgAccountId] = useState("");
  const [igToken, setIgToken] = useState("");

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await api.put('/api/v1/business', {
        whatsapp_phone_id: waPhoneId,
        whatsapp_token: waToken,
        ig_account_id: igAccountId,
        ig_access_token: igToken
      });
      setUpdated(true);
      setTimeout(() => setUpdated(false), 3000);
    } catch (error) {
      console.error("Failed to update integrations", error);
      alert("Failed to save settings");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center gap-2">
        <Smartphone className="h-6 w-6 text-primary-600" />
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Social Integrations</h1>
      </div>
      <p className="text-muted-foreground">Connect your APIs to automate messaging and social media publishing.</p>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Smartphone className="h-5 w-5 text-green-600" />
            <CardTitle>WhatsApp Business API</CardTitle>
          </div>
          <CardDescription>Connect your WhatsApp to enable auto-publishing.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>WhatsApp Phone Number ID</Label>
            <Input 
              placeholder="e.g. 10234567890" 
              value={waPhoneId}
              onChange={(e) => setWaPhoneId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Permanent Access Token</Label>
            <Input 
              type="password" 
              placeholder="EAA..." 
              value={waToken}
              onChange={(e) => setWaToken(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Instagram className="h-5 w-5 text-pink-600" />
            <CardTitle>Instagram Graph API</CardTitle>
          </div>
          <CardDescription>Connect your Instagram Business account to auto-publish Posts and Reels.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Instagram Account ID</Label>
            <Input 
              placeholder="e.g. 178414..." 
              value={igAccountId}
              onChange={(e) => setIgAccountId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Permanent Access Token</Label>
            <Input 
              type="password" 
              placeholder="EAA..." 
              value={igToken}
              onChange={(e) => setIgToken(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Button onClick={handleUpdate} disabled={isUpdating} className="w-full">
        {isUpdating ? (
          <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
        ) : updated ? (
          <><Check className="mr-2 h-4 w-4" /> Integrations Saved</>
        ) : (
          "Save Integrations"
        )}
      </Button>
    </div>
  );
}
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
