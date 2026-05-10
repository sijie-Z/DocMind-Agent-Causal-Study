import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

export interface DemoSeedResponse {
  success: boolean
  message: string
  skipped?: boolean
  data?: {
    documents_created: number
    conversation_id: string
    conversation_title: string
  }
}

export const seedDemoData = async (): Promise<AxiosResponse<DemoSeedResponse>> => {
  return request.post('/demo/seed')
}

export const clearDemoData = async (): Promise<AxiosResponse<DemoSeedResponse>> => {
  return request.delete('/demo/seed')
}
