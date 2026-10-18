import { useState } from 'react';
import { Download, Loader2, FileDown, AlertCircle, ChevronDown } from 'lucide-react';
import { generateBulkBBLV, downloadFileHelper } from '../api/siteApi';

export default function BulkExportBBLV() {
    const [inputVal, setInputVal] = useState('');
    const [representative, setRepresentative] = useState('Lê Thanh Quang');
    const [scenario, setScenario] = useState('auto');
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [result, setResult] = useState<{ downloadUrl: string; count: number; errors: string[] } | null>(null);

    const handleGenerate = async () => {
        setErrorMsg('');
        setResult(null);

        // Parse list of sites
        const siteIds = inputVal
            .split('\n')
            .map(id => id.trim().toUpperCase())
            .filter(id => id.length > 0);

        if (siteIds.length === 0) {
            setErrorMsg('Vui lòng nhập ít nhất một mã trạm.');
            return;
        }

        setLoading(true);
        try {
            const data = await generateBulkBBLV(siteIds, representative, scenario);
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
                            <h2 className="text-lg font-black text-slate-800">Xuất Hàng Loạt Biên Bản Làm Việc (BBLV Lần 4)</h2>
                            <p className="text-xs text-slate-500 font-medium mt-1">
                                Tự động tạo hàng loạt Biên Bản Làm Việc dựa vào mẫu BBLV.docx.
                            </p>
                        </div>
                        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
                            <FileDown className="w-6 h-6" />
                        </div>
                    </div>

                    <div className="p-6 space-y-5">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Dropdown Đại diện bên A */}
                            <div className="space-y-1 text-left">
                                <label className="text-[11px] font-black text-slate-500 uppercase block">Đại Diện Bên A (MobiFone)</label>
                                <div className="relative">
                                    <select
                                        value={representative}
                                        onChange={e => setRepresentative(e.target.value)}
                                        className="w-full bg-white border border-slate-200 text-xs font-black text-slate-700 rounded-lg px-2.5 py-2.5 appearance-none focus:outline-none focus:border-blue-500 cursor-pointer shadow-sm"
                                    >
                                        <option value="Lê Thanh Quang">Lê Thanh Quang</option>
                                        <option value="Lê Tân Cảng">Lê Tân Cảng</option>
                                        <option value="Trần Đăng Phan">Trần Đăng Phan</option>
                                    </select>
                                    <ChevronDown className="absolute right-3 top-3.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
                                </div>
                            </div>

                            {/* Dropdown Kịch bản Biên bản (BBLV Scenario Override) */}
                            <div className="space-y-1 text-left">
                                <label className="text-[11px] font-black text-slate-500 uppercase block">Kịch bản Biên Bản</label>
                                <div className="relative">
                                    <select
                                        value={scenario}
                                        onChange={e => setScenario(e.target.value)}
                                        className="w-full bg-white border border-slate-200 text-xs font-black text-slate-700 rounded-lg px-2.5 py-2.5 appearance-none focus:outline-none focus:border-blue-500 cursor-pointer shadow-sm"
                                    >
                                        <option value="auto">🤖 Tự động rẽ nhánh</option>
                                        <option value="giam_gia">📉 Kịch bản giảm giá thuê</option>
                                        <option value="gia_han">⏳ Kịch bản gia hạn/ký lại</option>
                                    </select>
                                    <ChevronDown className="absolute right-3 top-3.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
                                </div>
                            </div>
                        </div>

                        <div className="text-left">
                            <label className="block text-sm font-bold text-slate-700 mb-2">
                                Danh sách mã trạm (Copy dán hoặc nhập thủ công)
                            </label>
                            <textarea
                                className="w-full h-48 p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white resize-y"
                                placeholder="Ví dụ:&#10;DNDQ51&#10;DNCM11&#10;DNXX01..."
                                value={inputVal}
                                onChange={e => setInputVal(e.target.value)}
                            />
                            <p className="text-[#94A3B8] text-[11px] font-medium mt-2">
                                Mỗi mã trạm nằm trên một dòng. Trạm MobiFone sẽ tự động tính cộng thêm 600K guard/operations fee.
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
                            {loading ? 'Đang soạn thảo file Word...' : '🚀 BẮT ĐẦU XUẤT FILE HÀNG LOẠT'}
                        </button>

                        {result && (
                            <div className="mt-8 p-6 bg-[#F8FAFC] border border-blue-100 rounded-2xl">
                                <div className="flex items-center justify-between">
                                    <div className="text-left">
                                        <h3 className="text-base font-black text-slate-800">✅ Xử lý hoàn tất!</h3>
                                        <p className="text-sm text-slate-600 font-medium mt-1">Đã soạn thành công <strong className="text-blue-600">{result.count}</strong> Biên bản làm việc.</p>
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
                                    <div className="mt-6 text-left">
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
