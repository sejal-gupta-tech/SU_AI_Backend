import sys
import os

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\services\social.service.ts'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """  async publishToFacebook(contentId: string): Promise<any> {
    const res = await api.post(`/api/v1/social/publish-facebook/${contentId}`);
    return res.data;
  }
};"""

replacement = """  async publishToFacebook(contentId: string): Promise<any> {
    const res = await api.post(`/api/v1/social/publish-facebook/${contentId}`);
    return res.data;
  },

  async publishToLinkedin(contentId: string): Promise<any> {
    const res = await api.post(`/api/v1/social/publish-linkedin/${contentId}`);
    return res.data;
  }
};"""

content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
