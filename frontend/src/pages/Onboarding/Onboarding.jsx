// src/pages/Onboarding/Onboarding.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Users, Globe } from 'lucide-react';
import Button from '@/components/common/Button';

const Onboarding = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;
  
  const steps = [
    {
      title: 'Privacy First',
      titleColor: 'text-headline',
      description: 'Your data is secure. We prioritize candidate privacy and adhere to strict compliance standards.',
      icon: <Shield className="w-16 h-16 text-headline" />,
    },
    {
      title: 'Mutual Benefit',
      titleColor: 'text-secondary',
      description: 'Share your talent, gain access to a broader, verified pool of high-quality candidates.',
      icon: <Users className="w-16 h-16 text-secondary" />,
    },
    {
      title: 'Real-time Data',
      titleColor: 'text-headline',
      description: 'Leverage AI-powered insights for instant access to market-relevant talent information.',
      icon: <Globe className="w-16 h-16 text-headline" />,
    },
  ];
  
  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete onboarding
      localStorage.setItem('onboarding_completed', 'true');
      navigate('/dashboard');
    }
  };
  
  const handleSkip = () => {
    localStorage.setItem('onboarding_completed', 'true');
    navigate('/dashboard');
  };
  
  const currentStepData = steps[currentStep - 1];
  const progress = (currentStep / totalSteps) * 100;
  
  return (
    <div className="min-h-screen bg-background flex flex-col p-4">
      {/* Top Logo */}
      <div className="p-4">
        <h1 className="text-2xl font-display font-bold italic text-headline">
          TalentGrid
        </h1>
      </div>

      <div className="flex-1 flex items-center justify-center">
      <div className="w-full max-w-4xl">
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <span className="text-2xl font-bold text-text-primary">{Math.round(progress)}%</span>
            <span className="text-sm text-text-secondary">Step {currentStep} of {totalSteps}: {currentStep === 1 ? 'Welcome' : currentStep === 2 ? 'Benefits' : 'Get Started'}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        
        {/* Content Card */}
        <div className="bg-white rounded-2xl shadow-xl p-12 text-center animate-fade-in">
          {/* Main Heading */}
          <h2 className="text-4xl font-display font-bold text-text-primary mb-4">
            Everyone benefits from a stronger shared pool
          </h2>
          
          <p className="text-lg text-text-secondary mb-12">
            Join our network to access the best talent with trust and transparency.
          </p>
          
          {/* Three Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`flex flex-col items-center transition-all duration-300 ${
                  index + 1 === currentStep ? 'scale-110' : 'opacity-50'
                }`}
              >
                <div className="mb-4">
                  {step.icon}
                </div>
                <h3 className={`text-xl font-bold ${step.titleColor} mb-2`}>
                  {step.title}
                </h3>
                <p className="text-sm text-text-secondary">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
          
          {/* Buttons */}
          <div className="flex gap-4 justify-center">
            <Button
              variant="secondary"
              size="lg"
              onClick={handleNext}
              className="px-12"
            >
              {currentStep === totalSteps ? 'Get Started' : 'Continue'}
            </Button>
          </div>
          
          {/* Skip Link */}
          <button
            onClick={handleSkip}
            className="mt-6 text-headline hover:text-primary transition-colors underline"
          >
            Skip for now
          </button>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Onboarding;