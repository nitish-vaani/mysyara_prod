export type CreateUserRequest = {
    user_id: string,
    username: string,
    contact_number: string,
    password: string
  }

export type LoginRequest = { username: string, password: string }

export type LoginResponse = { message: string, user_id: string }

export type TriggerCallRequest = {
        user_id: string,
        agent_id: string,
        name: string,
        contact_number: string
}

export type FeedbackRequest = {
    conversation_id: string,
    user_id: string,
    feedback_text: string,
    felt_natural: number,
    response_speed: number,
    interruptions: number,
}

// Dashboard types
export type DashboardMetrics = {
    total_calls: number,
    // total_leads: number,
    // conversion_rate: number,
    avg_call_duration: number,
    total_call_duration: number
}
export type TrendData = {
    date: string,
    calls: number,
    leads: number,
    duration: number
}

export type DashboardResponse = {
    metrics: DashboardMetrics,
    call_trends: TrendData[],
    lead_trends: TrendData[],
    period: string
}