# Plan: Contract Management Features
Created: 2026-05-07
Status: 🟡 In Progress

## Overview
Hoàn thiện và đóng gói 3 nhóm tính năng cốt lõi cho ứng dụng Quản lý Hợp đồng Nhà trạm:
1. Nhóm Rà soát (Lọc tổ, hết hạn, ngoài khung giá).
2. Nhóm Đàm phán & Phụ lục (Theo dõi tiến độ, Sinh file Word tự động).
3. Nhóm Thanh toán (Quản lý trạm chưa thanh toán, chốt hồ sơ).

## Tech Stack
- Frontend: React + TypeScript + Vite + TailwindCSS
- Backend: Python + FastAPI
- Database: Hiện tại là Google Sheets (qua Apps Script) & Excel nội bộ.
- Sinh file: `docxtpl` trên Python Backend.

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Setup & Đánh giá hiện trạng | ⬜ Pending | 0% |
| 02 | Hoàn thiện bộ lọc & Dashboard (Rà soát) | ⬜ Pending | 0% |
| 03 | Xử lý sinh File Word tự động (Phụ lục) | ⬜ Pending | 0% |
| 04 | Chốt luồng Thanh toán & Tracking | ⬜ Pending | 0% |
| 05 | Testing & Bàn giao | ⬜ Pending | 0% |

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
