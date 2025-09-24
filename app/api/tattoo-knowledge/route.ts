import { NextRequest, NextResponse } from 'next/server';
import { apiPipeline } from '../../lib/api-pipeline';

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    const result = await apiPipeline.processRequest('tattoo_knowledge', request, data);
    
    if (result.success) {
      return NextResponse.json(result.data, { status: 200 });
    } else {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Tattoo knowledge API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const pipelineInfo = apiPipeline.getPipelineInfo('tattoo_knowledge');
    
    return NextResponse.json({
      pipeline: 'tattoo_knowledge',
      info: pipelineInfo,
      status: 'active'
    });
  } catch (error) {
    console.error('Tattoo knowledge API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
