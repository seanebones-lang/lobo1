import { NextRequest, NextResponse } from 'next/server';
import { apolloBuildAssessor } from '../../../lib/apollo-build-assessor';

export async function GET(request: NextRequest) {
  try {
    console.log('🌊 APOLLO Build Assessment: Starting comprehensive analysis...');
    
    const assessment = apolloBuildAssessor.assessBuild();
    const fixCommands = apolloBuildAssessor.generateFixCommands();
    const healthCheck = apolloBuildAssessor.generateHealthCheck();
    
    const apolloResponse = {
      timestamp: new Date().toISOString(),
      version: 'APOLLO-1.0.0',
      assessment,
      fixCommands,
      healthCheck,
      metadata: {
        assessor: 'APOLLO Build Assessment System',
        confidence: 0.95,
        processingTime: Date.now()
      }
    };
    
    console.log(`🌊 APOLLO Assessment Complete: Score ${assessment.overallScore}/100, Status: ${assessment.status}`);
    
    return NextResponse.json(apolloResponse, { 
      status: 200,
      headers: {
        'Cache-Control': 'no-cache',
        'X-APOLLO-Version': '1.0.0',
        'X-Assessment-Score': assessment.overallScore.toString()
      }
    });
  } catch (error) {
    console.error('❌ APOLLO Assessment Error:', error);
    
    return NextResponse.json(
      { 
        error: 'APOLLO assessment failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
        status: 'error'
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json();
    
    switch (action) {
      case 'fix-build':
        return NextResponse.json({
          message: 'APOLLO build fix commands generated',
          commands: apolloBuildAssessor.generateFixCommands(),
          timestamp: new Date().toISOString()
        });
        
      case 'health-check':
        return NextResponse.json({
          message: 'APOLLO health check script generated',
          script: apolloBuildAssessor.generateHealthCheck(),
          timestamp: new Date().toISOString()
        });
        
      case 'quick-fix':
        return NextResponse.json({
          message: 'APOLLO quick fix recommendations',
          fixes: [
            'kill -9 $(lsof -ti:8007) 2>/dev/null || true',
            'rm -rf .next node_modules package-lock.json',
            'npm install --legacy-peer-deps',
            'npm run build',
            'npm run dev -p 8007'
          ],
          timestamp: new Date().toISOString()
        });
        
      default:
        return NextResponse.json({
          error: 'Unknown action',
          availableActions: ['fix-build', 'health-check', 'quick-fix'],
          timestamp: new Date().toISOString()
        }, { status: 400 });
    }
  } catch (error) {
    console.error('❌ APOLLO Action Error:', error);
    
    return NextResponse.json(
      { 
        error: 'APOLLO action failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
