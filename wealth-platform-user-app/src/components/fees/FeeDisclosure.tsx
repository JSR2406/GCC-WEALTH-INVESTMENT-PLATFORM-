'use client';

import { useState, useEffect } from 'react';
import { calculateFee } from '@/lib/api-client';

interface FeeDisclosureProps {
    feeCode: string;
    quantity?: number;
    baseAmount?: number;
    onAccept?: () => void;
    onDecline?: () => void;
}

export function FeeDisclosure({
    feeCode,
    quantity = 1,
    baseAmount = 0,
    onAccept,
    onDecline
}: FeeDisclosureProps) {
    const [feeDetails, setFeeDetails] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchFee() {
            try {
                const details = await calculateFee({
                    fee_code: feeCode,
                    quantity,
                    base_amount: baseAmount
                });
                setFeeDetails(details);
            } catch (error) {
                console.error('Failed to calculate fee:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchFee();
    }, [feeCode, quantity, baseAmount]);

    if (loading) {
        return <div className="animate-pulse">Calculating fee...</div>;
    }

    if (!feeDetails) {
        return null;
    }

    return (
        <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">
                        Service Fee
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                        {feeDetails.description}
                    </p>

                    <div className="mt-4 space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Base Amount:</span>
                            <span className="font-medium">
                                ${baseAmount.toFixed(2)}
                            </span>
                        </div>

                        {quantity > 1 && (
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Quantity:</span>
                                <span className="font-medium">{quantity}</span>
                            </div>
                        )}

                        <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Service Fee:</span>
                            <span className="font-medium">
                                ${feeDetails.fee_amount.toFixed(2)}
                            </span>
                        </div>

                        {feeDetails.breakdown?.rate && (
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Rate:</span>
                                <span className="font-medium">
                                    {feeDetails.breakdown.rate}%
                                </span>
                            </div>
                        )}

                        <div className="border-t pt-2 flex justify-between font-semibold">
                            <span>Total Amount:</span>
                            <span className="text-lg text-blue-600">
                                ${(baseAmount + feeDetails.fee_amount).toFixed(2)}
                            </span>
                        </div>
                    </div>

                    {!feeDetails.is_optional && (
                        <p className="text-xs text-gray-500 mt-3">
                            * This fee is required for this service
                        </p>
                    )}
                </div>
            </div>

            <div className="mt-4 flex gap-3">
                {onAccept && (
                    <button
                        onClick={onAccept}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                        Accept & Continue
                    </button>
                )}

                {feeDetails.is_optional && onDecline && (
                    <button
                        onClick={onDecline}
                        className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                    >
                        Decline
                    </button>
                )}
            </div>
        </div>
    );
}
