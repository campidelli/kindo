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
  booking_id: string;
  card_number: string;
  expiry_month: number;
  expiry_year: number;
  cvv: string;
}

export interface BookingResponse {
  id: string;
  trip_id: string;
  status: string;
  parent_name: string;
  child_name: string;
  created_at: string;
}

export interface PaymentResponse {
  id: string;
  booking_id: string;
  status: string;
  card_last_four: string;
  transaction_id: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ReceiptTrip {
  id: string;
  title: string;
  description: string;
  date: string;
  location: string;
  cost: number;
  school_id: string;
  activity_id: string;
}

export interface ReceiptBooking {
  id: string;
  trip_id: string;
  status: string;
  parent_name: string;
  child_name: string;
  created_at: string;
}

export interface ReceiptPayment {
  id: string;
  booking_id: string;
  card_last_four: string;
  status: string;
  transaction_id: string | null;
  error_message: string | null;
  created_at: string;
}

export interface BookingReceiptResponse {
  booking: ReceiptBooking;
  trip: ReceiptTrip;
  payment: ReceiptPayment;
}
