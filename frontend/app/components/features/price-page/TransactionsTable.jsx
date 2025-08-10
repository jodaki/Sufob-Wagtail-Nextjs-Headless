"use client";

import React, { useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

const TransactionsTable = ({ transactionsList = null, itemsPerPage = 10 }) => {
  
  // Default transactions data
  const defaultTransactions = [
    {
      id: 1,
      row: '1',
      date: '1404/04/30',
      time: '09:00',
      volume: '45,000',
      price: '54,540',
      totalValue: '2,454,300,000',
      buyer: 'خریدار الف',
      seller: 'فروشنده ب'
    },
    {
      id: 2,
      row: '2',
      date: '1404/04/30',
      time: '09:15',
      volume: '30,000',
      price: '54,600',
      totalValue: '1,638,000,000',
      buyer: 'خریدار ج',
      seller: 'فروشنده د'
    },
    {
      id: 3,
      row: '3',
      date: '1404/04/30',
      time: '09:30',
      volume: '25,000',
      price: '54,450',
      totalValue: '1,361,250,000',
      buyer: 'خریدار ه',
      seller: 'فروشنده و'
    },
    {
      id: 4,
      row: '4',
      date: '1404/04/30',
      time: '10:00',
      volume: '35,000',
      price: '54,700',
      totalValue: '1,914,500,000',
      buyer: 'خریدار ز',
      seller: 'فروشنده ح'
    },
    {
      id: 5,
      row: '5',
      date: '1404/04/30',
      time: '10:15',
      volume: '20,000',
      price: '54,800',
      totalValue: '1,096,000,000',
      buyer: 'خریدار ط',
      seller: 'فروشنده ی'
    },
    {
      id: 6,
      row: '6',
      date: '1404/04/30',
      time: '10:30',
      volume: '40,000',
      price: '54,650',
      totalValue: '2,186,000,000',
      buyer: 'خریدار ک',
      seller: 'فروشنده ل'
    }
  ];

  const transactions = transactionsList || defaultTransactions;
  const [currentPage, setCurrentPage] = useState(1);
  
  // Calculate pagination
  const totalPages = Math.ceil(transactions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTransactions = transactions.slice(startIndex, endIndex);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const goToPrevious = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const goToNext = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <TableContainer component={Paper} sx={{ width: '100%', boxShadow: 'none', borderRadius: 2, mt: 3 }}>
      <Typography variant="h6" sx={{ px: 2, py: 1, fontWeight: 600 }}>جدول معاملات اخیر</Typography>
      <Table sx={{ minWidth: 650 }} aria-label="transactions table">
        <TableHead>
          <TableRow>
            <TableCell>ردیف</TableCell>
            <TableCell>تاریخ</TableCell>
            <TableCell>زمان</TableCell>
            <TableCell>حجم</TableCell>
            <TableCell>قیمت</TableCell>
            <TableCell>ارزش کل</TableCell>
            <TableCell>خریدار</TableCell>
            <TableCell>فروشنده</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {currentTransactions.map((transaction) => (
            <TableRow key={transaction.id}>
              <TableCell>{transaction.row}</TableCell>
              <TableCell>{transaction.date}</TableCell>
              <TableCell>{transaction.time}</TableCell>
              <TableCell align="left">{transaction.volume}</TableCell>
              <TableCell align="left" sx={{ fontWeight: 'bold' }}>{transaction.price}</TableCell>
              <TableCell align="left">{transaction.totalValue}</TableCell>
              <TableCell>{transaction.buyer}</TableCell>
              <TableCell>{transaction.seller}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="d-flex justify-content-between align-items-center mt-3 px-2 pb-2">
          <div>
            صفحه {currentPage} از {totalPages} (کل {transactions.length} معامله)
          </div>
          <div className="btn-group" role="group">
            <button 
              type="button" 
              className="btn btn-outline-primary btn-sm"
              onClick={goToPrevious}
              disabled={currentPage === 1}
            >
              قبلی
            </button>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                type="button"
                className={`btn btn-sm ${currentPage === page ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => goToPage(page)}
              >
                {page}
              </button>
            ))}
            
            <button 
              type="button" 
              className="btn btn-outline-primary btn-sm"
              onClick={goToNext}
              disabled={currentPage === totalPages}
            >
              بعدی
            </button>
          </div>
        </div>
      )}
    </TableContainer>
  );
};

export default TransactionsTable;
