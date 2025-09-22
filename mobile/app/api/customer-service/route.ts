import { NextRequest, NextResponse } from 'next/server';
import { apiPipeline } from '../../lib/api-pipeline';

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    const result = await apiPipeline.processRequest('customer_service', request, data);
    
    if (result.success) {
      return NextResponse.json(result.data, { status: 200 });
    } else {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Customer service API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const pipelineInfo = apiPipeline.getPipelineInfo('customer_service');
    
    return NextResponse.json({
      pipeline: 'customer_service',
      info: pipelineInfo,
      status: 'active'
    });
  } catch (error) {
    console.error('Customer service API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
