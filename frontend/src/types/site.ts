export interface Site {
  site_id: string;
  owner: string;
  end_date: string;
  ext_status: string;
  old_price: number;
  new_price: number;
  dat_muc_tieu_1245?: string;
  duoc_thanh_toan_1245?: string;
  has_agreed_1245?: boolean;
  no_addendum_needed?: boolean;
  reached_target?: string;
  reduction_amount?: number;
  reduced_price?: number;
  negotiation_date?: string;
  effective_date?: string;
  prices_breakdown: {
    mb: number;
    pm: number;
    mfd: number;
    cot: number;
    giam_tru: number;
    cot_rounded: number;
  };
  payment_cycle: string;
  to_vt: string;
  site_type?: string;
  banking_info: {
    account_owner: string;
    account_no: string;
    bank_name: string;
    bank_branch: string;
    is_owner_match: boolean;
    match_status_text: string;
  };
  progress_tracker: {
    selected_template: string;
    status: string;
    new_contract_no?: string;
    new_contract_date?: string;
    new_price_confirmed?: number;
    last_updated?: string;
    progress: {
      draft_prepared: boolean;
      submitted_internal: boolean;
      signed_and_stamped: boolean;
      archived_doc: boolean;
    };
  };
}
