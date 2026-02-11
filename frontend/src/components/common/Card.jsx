// src/components/common/Card.jsx
import React from 'react';
import clsx from 'clsx';

const Card = ({
  children,
  className,
  hoverable = false,
  onClick,
  padding = true,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-gray-200',
        padding && 'p-6',
        hoverable && 'hover:shadow-lg hover:border-primary-200 cursor-pointer transition-all duration-200',
        'shadow-card',
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;