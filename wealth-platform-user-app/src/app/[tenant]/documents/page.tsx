'use client';

import { useState } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';

const mockDocuments = [
    {
        id: 'doc-1',
        name: 'Annual Portfolio Statement 2025',
        type: 'statement',
        size: '2.4 MB',
        date: '2026-01-15',
        status: 'ready'
    },
    {
        id: 'doc-2',
        name: 'Tax Summary Report 2025',
        type: 'tax',
        size: '1.8 MB',
        date: '2026-01-10',
        status: 'ready'
    },
    {
        id: 'doc-3',
        name: 'KYC Verification - Passport',
        type: 'kyc',
        size: '850 KB',
        date: '2025-06-20',
        status: 'verified'
    },
    {
        id: 'doc-4',
        name: 'Investment Agreement',
        type: 'legal',
        size: '1.2 MB',
        date: '2024-03-15',
        status: 'signed'
    },
    {
        id: 'doc-5',
        name: 'Zakat Certificate 1447H',
        type: 'certificate',
        size: '500 KB',
        date: '2025-04-01',
        status: 'ready'
    }
];

const documentIcons: Record<string, string> = {
    statement: '📊',
    tax: '📋',
    kyc: '🪪',
    legal: '📜',
    certificate: '🏅',
    other: '📄'
};

const filterOptions = [
    { value: 'all', label: 'All Documents' },
    { value: 'statement', label: 'Statements' },
    { value: 'tax', label: 'Tax Documents' },
    { value: 'kyc', label: 'KYC Documents' },
    { value: 'legal', label: 'Legal Documents' },
    { value: 'certificate', label: 'Certificates' }
];

export default function DocumentsPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [filter, setFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    const filteredDocuments = mockDocuments.filter(doc => {
        const matchesFilter = filter === 'all' || doc.type === filter;
        const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
                    <p className="text-gray-500 mt-1">Access your statements, reports, and legal documents</p>
                </div>
                <button
                    className="px-4 py-2 rounded-xl text-white font-medium transition-all hover:opacity-90 flex items-center gap-2"
                    style={{ backgroundColor: primaryColor }}
                >
                    <span>📤</span>
                    Upload Document
                </button>
            </div>

            {/* Search & Filter */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
                    <input
                        type="text"
                        placeholder="Search documents..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                    />
                </div>
                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none bg-white"
                >
                    {filterOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
            </div>

            {/* Documents List */}
            <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
                {filteredDocuments.length === 0 ? (
                    <div className="p-12 text-center">
                        <div className="text-5xl mb-4">📭</div>
                        <p className="text-gray-600 font-medium">No documents found</p>
                        <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filter</p>
                    </div>
                ) : (
                    <div className="divide-y">
                        {filteredDocuments.map((doc) => (
                            <div
                                key={doc.id}
                                className="p-4 hover:bg-gray-50 transition-colors flex items-center justify-between gap-4"
                            >
                                <div className="flex items-center gap-4">
                                    <div
                                        className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                                        style={{ backgroundColor: `${primaryColor}15` }}
                                    >
                                        {documentIcons[doc.type] || '📄'}
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900">{doc.name}</p>
                                        <div className="flex items-center gap-3 text-sm text-gray-500 mt-1">
                                            <span>{doc.size}</span>
                                            <span>•</span>
                                            <span>{new Date(doc.date).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                                year: 'numeric'
                                            })}</span>
                                            <span>•</span>
                                            <span
                                                className={`px-2 py-0.5 rounded-full text-xs font-medium ${doc.status === 'verified' ? 'bg-green-100 text-green-700' :
                                                        doc.status === 'signed' ? 'bg-blue-100 text-blue-700' :
                                                            'bg-gray-100 text-gray-600'
                                                    }`}
                                            >
                                                {doc.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                                        title="Preview"
                                    >
                                        👁️
                                    </button>
                                    <button
                                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                                        title="Download"
                                    >
                                        ⬇️
                                    </button>
                                    <button
                                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                                        title="Share"
                                    >
                                        📤
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <button className="bg-white rounded-xl border p-4 hover:shadow-md transition-all text-left group">
                    <div className="flex items-center gap-3">
                        <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform"
                            style={{ backgroundColor: `${primaryColor}15` }}
                        >
                            📊
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">Generate Statement</p>
                            <p className="text-sm text-gray-500">Create custom date range</p>
                        </div>
                    </div>
                </button>
                <button className="bg-white rounded-xl border p-4 hover:shadow-md transition-all text-left group">
                    <div className="flex items-center gap-3">
                        <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform"
                            style={{ backgroundColor: `${primaryColor}15` }}
                        >
                            📋
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">Request Tax Report</p>
                            <p className="text-sm text-gray-500">FATCA, CRS, or custom</p>
                        </div>
                    </div>
                </button>
                <button className="bg-white rounded-xl border p-4 hover:shadow-md transition-all text-left group">
                    <div className="flex items-center gap-3">
                        <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform"
                            style={{ backgroundColor: `${primaryColor}15` }}
                        >
                            🪪
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">Update KYC</p>
                            <p className="text-sm text-gray-500">Renew your documents</p>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
