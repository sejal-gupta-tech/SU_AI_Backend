import sys
import os

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\services\social.service.ts'

content = """import api from './api';

export const socialService = {
  async publishToWhatsApp(contentId: string, targetPhone: string): Promise<any> {
    const res = await api.post(`/api/v1/social/publish-whatsapp/${contentId}`, {
      target_phone: targetPhone
    });
    return res.data;
  }
};
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
