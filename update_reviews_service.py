import sys
import os

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\services\reviews.service.ts'

new_content = """import { Review } from '@/types/reviews';
import api from './api';

export const reviewsService = {
  async getReviews(): Promise<{ data: Review[] }> {
    const res = await api.get('/api/v1/reviews');
    // Map snake_case from backend to camelCase for frontend
    const mappedData = res.data.data.map((r: any) => ({
      ...r,
      _id: r.id,
      customerName: r.customer_name,
      reviewText: r.review_text,
      createdAt: r.created_at,
      updatedAt: r.updated_at
    }));
    return { data: mappedData };
  },

  async generateReply(reviewId: string): Promise<{ data: string }> {
    const res = await api.post(`/api/v1/reviews/${reviewId}/generate-reply`);
    return res.data;
  },

  async sendReply(reviewId: string, replyText: string): Promise<{ data: Review }> {
    const res = await api.put(`/api/v1/reviews/${reviewId}`, {
      status: 'Replied',
      reply: replyText
    });
    const r = res.data.data;
    return { 
      data: {
        ...r,
        _id: r.id,
        customerName: r.customer_name,
        reviewText: r.review_text,
        createdAt: r.created_at,
        updatedAt: r.updated_at
      } 
    };
  }
};
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Frontend reviews service updated successfully.")
