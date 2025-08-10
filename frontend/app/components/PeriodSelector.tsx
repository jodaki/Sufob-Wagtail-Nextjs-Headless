"use client";

interface PeriodSelectorProps {
    currentPeriod: string;
    onPeriodChange: (period: string) => void;
    disabled?: boolean;
}

export default function PeriodSelector({ currentPeriod, onPeriodChange, disabled = false }: PeriodSelectorProps) {
    const periods = [
        { key: 'daily', label: '1D' },
        { key: 'weekly', label: '1W' },
        { key: 'monthly', label: '1M' },
        { key: 'yearly', label: '1Y' }
    ];

    const intervalColors: { [key: string]: string } = {
        'daily': '#2962FF',
        'weekly': 'rgb(225, 87, 90)',
        'monthly': 'rgb(242, 142, 44)',
        'yearly': 'rgb(164, 89, 209)',
    };

    return (
        <div className="mb-6">
            <div className="flex gap-2">
                {periods.map((period) => (
                    <button
                        key={period.key}
                        onClick={() => onPeriodChange(period.key)}
                        disabled={disabled}
                        className={`
                            px-6 py-2 font-medium rounded-lg transition-all duration-200
                            ${currentPeriod === period.key
                                ? 'text-white shadow-lg'
                                : 'text-gray-700 bg-gray-100 hover:bg-gray-200'
                            }
                            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                        `}
                        style={{
                            backgroundColor: currentPeriod === period.key 
                                ? intervalColors[period.key] 
                                : undefined
                        }}
                    >
                        {period.label}
                    </button>
                ))}
            </div>
        </div>
    );
}
