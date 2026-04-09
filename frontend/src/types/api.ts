export interface TripResponse {
  id: string;
  title: string;
  description: string;
  date: string;
  location: string;
  cost: number;
  school_id: string;
  activity_id: string;
  created_at: string;
}

export interface PaymentRequest {
  trip_id: string;
  student_name: string;
  parent_name: string;
  card_number: string;
  expiry_date: string;
  cvv: string;
}

export interface PaymentCreatedResponse {
  payment_id: string;
  status: string;
  trip_id: string;
  created_at: string;
}

export interface PaymentDetailResponse {
  id: string;
  trip_id: string;
  student_name: string;
  parent_name: string;
  card_last_four: string;
  status: string;
  transaction_id: string | null;
  error_message: string | null;
  created_at: string;
}
