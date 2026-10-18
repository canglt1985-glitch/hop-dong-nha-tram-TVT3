import { useState } from 'react';
import { Download, Loader2, FileDown, AlertCircle } from 'lucide-react';
import { generateBulkCct, downloadFileHelper } from '../api/siteApi';

export default function BulkExportCCT() {
    const [inputVal, setInputVal] = useState('');
    const [loading, setLoading] = useState(false);
    const [party, setParty] = useState<'A' | 'B'>('B');
    const [includeExtension, setIncludeExtension] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [result, setResult] = useState<{ downloadUrl: string; count: number; errors: string[] } | null>(null);

    const handleGenerate = async () => {
        setErrorMsg('');
        setResult(null);

        // Parse input into an array of lines/IDs
        const siteIds = inputVal
            .split('\n')
            .map(id => id.trim())
            .filter(id => id.length > 0);

        if (siteIds.length === 0) {
            setErrorMsg('Vui lòng nhập ít nhất một mã trạm.');
            return;
        }

        setLoading(true);
        try {
            const data = await generateBulkCct(siteIds, party, includeExtension);
            setResult({
                downloadUrl: `/api/download/${data.filename}`,
                count: data.count,
                errors: data.errors || [],
            });
        } catch (err: any) {
            setErrorMsg(err.message || 'Có lỗi xảy ra khi gọi máy chủ.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 p-8 bg-slate-50 overflow-y-auto">
            <div className="max-w-4xl mx-auto space-y-6">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                    <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-black text-slate-800">Xuất Hàng Loạt Phụ Lục Chuyển Chủ Thể</h2>
                            <p className="text-xs text-slate-500 font-medium mt-1">
                                Tự động tạo file Word cho nhiều trạm điện thoại đàm phán chuyển nhượng.
                            </p>
                        </div>
                        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
                            <FileDown className="w-6 h-6" />
                        </div>
                    </div>

                    <div className="p-6 space-y-5">
                        {/* Selector A/B */}
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">
                                Chọn chủ thể chuyển nhượng
                            </label>
                            <div className="grid grid-cols-2 gap-2 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
                                <button
                                    type="button"
                                    onClick={() => { setParty('A'); setResult(null); }}
                                    className={`py-3 text-sm font-bold rounded-lg transition-all cursor-pointer ${party === 'A'
                                        ? 'bg-white text-blue-600 shadow-sm border border-slate-200'
                                        : 'text-slate-500 hover:text-slate-750'
                                        }`}
                                >
                                    👤 Bên A (Chủ cho thuê / Chủ đất)
                                </button>
                                <button
                                    type="button"
                                    onClick={() => { setParty('B'); setResult(null); }}
                                    className={`py-3 text-sm font-bold rounded-lg transition-all cursor-pointer ${party === 'B'
                                        ? 'bg-white text-blue-600 shadow-sm border border-slate-200'
                                        : 'text-slate-500 hover:text-slate-750'
                                        }`}
                                >
                                    🏢 Bên B (Đơn vị thuê / MobiFone)
                                </button>
                            </div>
                            <p className="text-[11px] text-[#64748B] font-medium mt-2">
                                {party === 'A'
                                    ? '👉 Kịch bản thay đổi chủ thể sở hữu khu đất thuê (sử dụng mẫu PHU_LUC_CHUYEN_CHU_THE_BEN_A.docx)'
                                    : '👉 Kịch bản chuyển giao chi nhánh MobiFone đàm phán thuê trạm (sử dụng mẫu PHU_LUC_CHUYEN_CHU_THE.docx)'}
                            </p>

                            <div className="flex items-center gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200 mt-4">
                                <input
                                    type="checkbox"
                                    id="include_extension"
                                    checked={includeExtension}
                                    onChange={(e) => setIncludeExtension(e.target.checked)}
                                    className="w-5 h-5 text-blue-600 rounded cursor-pointer"
                                />
                                <label htmlFor="include_extension" className="text-sm font-bold text-slate-700 cursor-pointer">
                                    Gắn kèm Gia hạn hợp đồng (+) 5 năm
                                </label>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">
                                Danh sách mã trạm (Copy dán hoặc nhập thủ công)
                            </label>
                            <textarea
                                className="w-full h-48 p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white resize-y"
                                placeholder="Ví dụ:&#10;DNCM36&#10;DNLK60&#10;DNXX01..."
                                value={inputVal}
                                onChange={e => setInputVal(e.target.value)}
                            />
                            <p className="text-[#94A3B8] text-[11px] font-medium mt-2">
                                Mỗi mã trạm nằm trên một dòng. Có thể copy nguyên cột từ Excel để dán thẳng vào ô này.
                            </p>
                        </div>

                        {errorMsg && (
                            <div className="p-4 bg-red-50 text-red-600 text-sm font-bold rounded-xl border border-red-100 flex items-center gap-3">
                                <AlertCircle className="w-5 h-5 shrink-0" />
                                {errorMsg}
                            </div>
                        )}

                        <button
                            disabled={loading}
                            onClick={handleGenerate}
                            className="w-full flex items-center justify-center gap-2 py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold rounded-xl transition-all cursor-pointer"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Download className="w-5 h-5" />
                            )}
                            {loading ? 'Đang soạn thảo file Word...' : `🚀 BẮT ĐẦU XUẤT FILE HÀNG LOẠT (BÊN ${party})`}
                        </button>

                        {result && (
                            <div className="mt-8 p-6 bg-[#F8FAFC] border border-blue-100 rounded-2xl">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-base font-black text-slate-800">✅ Xử lý hoàn tất!</h3>
                                        <p className="text-sm text-slate-600 font-medium mt-1">Đã soạn thành công <strong className="text-blue-600">{result.count}</strong> phụ lục.</p>
                                    </div>
                                    <button
                                        onClick={() => downloadFileHelper(result.downloadUrl)}
                                        className="flex items-center gap-2 px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-bold rounded-xl transition-all cursor-pointer"
                                    >
                                        <Download className="w-4 h-4" />
                                        Tải File ZIP Xuống
                                    </button>
                                </div>

                                {result.errors.length > 0 && (
                                    <div className="mt-6">
                                        <h4 className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                                            <AlertCircle className="w-4 h-4 text-orange-500" />
                                            Một số trạm gặp lỗi hoặc không tìm thấy:
                                        </h4>
                                        <ul className="space-y-1.5 p-4 bg-white border border-slate-200 rounded-xl max-h-40 overflow-y-auto">
                                            {result.errors.map((err, i) => (
                                                <li key={i} className="text-xs font-medium text-slate-600 font-mono">
                                                    {err}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
