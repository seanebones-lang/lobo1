import { NextRequest, NextResponse } from 'next/server';
import { apiPipeline } from '../../../lib/api-pipeline';
import { ragPipeline } from '../../../lib/rag-pipeline';

export async function GET(request: NextRequest) {
  try {
    const allPipelines = apiPipeline.getAllPipelines();
    const ragStats = ragPipeline.getPipelineStats();
    const cacheStats = apiPipeline.getCacheStats();
    
    const pipelineStatus = Array.from(allPipelines.entries()).map(([name, config]) => ({
      name,
      config,
      status: 'active',
      lastChecked: new Date().toISOString()
    }));
    
    const ragStatus = {
      totalPipelines: ragStats.totalPipelines,
      availablePipelines: ragStats.pipelines,
      knowledgeBaseSize: ragStats.knowledgeBaseSize,
      status: 'active'
    };
    
    const systemStatus = {
      timestamp: new Date().toISOString(),
      status: 'operational',
      pipelines: {
        api: pipelineStatus,
        rag: ragStatus
      },
      cache: cacheStats,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      version: 'APOLLO-1.0.0'
    };
    
    return NextResponse.json(systemStatus, { status: 200 });
  } catch (error) {
    console.error('Pipeline status API error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        status: 'error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
