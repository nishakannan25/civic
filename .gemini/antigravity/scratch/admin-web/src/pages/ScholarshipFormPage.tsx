import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Sparkles, AlertCircle, Info } from 'lucide-react';
import { useScholarship, useCreateScholarship, useUpdateScholarship } from '../hooks/useScholarships';
import { EducationLevel, ScholarshipCategory, ScholarshipItem } from '../types';

export const ScholarshipFormPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);

  const { data: existing, isLoading: isFetching } = useScholarship(id || '');
  const createMutation = useCreateScholarship();
  const updateMutation = useUpdateScholarship();

  const [title, setTitle] = useState('');
  const [provider, setProvider] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState<number>(50000);
  const [deadline, setDeadline] = useState('');
  const [educationLevels, setEducationLevels] = useState<EducationLevel[]>(['Undergraduate']);
  const [categories, setCategories] = useState<ScholarshipCategory[]>(['Merit-Based']);
  const [regionsInput, setRegionsInput] = useState('National, State-Level');
  const [eligibleRolesInput, setEligibleRolesInput] = useState('STUDENT');
  const [tagsInput, setTagsInput] = useState('Merit, Financial Aid');
  const [documentsInput, setDocumentsInput] = useState('Income Certificate, National ID, Academic Record');

  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (existing) {
      setTitle(existing.title);
      setProvider(existing.provider);
      setDescription(existing.description);
      setAmount(existing.amount);
      setDeadline(existing.deadline);
      setEducationLevels(existing.educationLevels);
      setCategories(existing.categories);
      setRegionsInput(existing.regions.join(', '));
      setEligibleRolesInput(existing.eligibleRoles.join(', '));
      setTagsInput(existing.tags.join(', '));
      setDocumentsInput(existing.requiredDocuments.join(', '));
    }
  }, [existing]);

  const toggleEducationLevel = (lvl: EducationLevel) => {
    setEducationLevels((prev) =>
      prev.includes(lvl) ? prev.filter((item) => item !== lvl) : [...prev, lvl]
    );
  };

  const toggleCategory = (cat: ScholarshipCategory) => {
    setCategories((prev) =>
      prev.includes(cat) ? prev.filter((item) => item !== cat) : [...prev, cat]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!title.trim()) {
      setValidationError('Scholarship title is required.');
      return;
    }
    if (!provider.trim()) {
      setValidationError('Provider organization name is required.');
      return;
    }
    if (amount <= 0) {
      setValidationError('Scholarship amount must be greater than 0.');
      return;
    }
    if (!deadline) {
      setValidationError('Application deadline date is required.');
      return;
    }
    if (educationLevels.length === 0) {
      setValidationError('Select at least one eligible education level.');
      return;
    }
    if (categories.length === 0) {
      setValidationError('Select at least one category.');
      return;
    }

    const payload = {
      title: title.trim(),
      provider: provider.trim(),
      description: description.trim(),
      amount,
      deadline,
      educationLevels,
      categories,
      regions: regionsInput.split(',').map((s) => s.trim()).filter(Boolean),
      eligibleRoles: eligibleRolesInput.split(',').map((s) => s.trim()).filter(Boolean),
      tags: tagsInput.split(',').map((s) => s.trim()).filter(Boolean),
      requiredDocuments: documentsInput.split(',').map((s) => s.trim()).filter(Boolean),
    };

    try {
      if (isEdit && id) {
        await updateMutation.mutateAsync({ id, data: payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      navigate('/scholarships');
    } catch (err: any) {
      setValidationError(err.message || 'Failed to save scholarship program.');
    }
  };

  if (isEdit && isFetching) {
    return (
      <div className="p-8 text-center text-slate-400">
        Loading scholarship record details...
      </div>
    );
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-10">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/scholarships')}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scholarships</span>
        </button>

        <h2 className="text-xl font-bold tracking-tight">
          {isEdit ? `Edit Scholarship — ${id}` : 'Create New Scholarship Program'}
        </h2>
      </div>

      {/* Fact Versioning Note */}
      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-600 dark:text-blue-300 flex items-start space-x-2.5">
        <Info className="w-4 h-4 shrink-0 text-blue-500 mt-0.5" />
        <div>
          <strong className="font-semibold">Fact Versioning Governance:</strong> Edits to scholarship amounts, eligibility rules, or qualification criteria will automatically update rule evaluator references in the <strong>VeriFlow engine</strong> without overwriting historical audit snapshots.
        </div>
      </div>

      {/* Error Alert */}
      {validationError && (
        <div className="p-3.5 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Form Card */}
      <form onSubmit={handleSubmit} className="p-6 rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 space-y-6 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Title */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Scholarship Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. National Merit STEM Fellowship 2026"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Provider */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Provider Organization *
            </label>
            <input
              type="text"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              placeholder="e.g. Ministry of Higher Education"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
            Description
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detailed description of scholarship purpose, eligibility overview, and disbursement terms..."
            className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Amount */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Grant Amount (INR ₹) *
            </label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              placeholder="150000"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Application Deadline *
            </label>
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Education Levels */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
            Eligible Education Levels *
          </label>
          <div className="flex flex-wrap gap-2">
            {(['Secondary', 'Vocational', 'Undergraduate', 'Postgraduate', 'Doctoral'] as EducationLevel[]).map((lvl) => {
              const active = educationLevels.includes(lvl);
              return (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => toggleEducationLevel(lvl)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors border ${
                    active
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {lvl}
                </button>
              );
            })}
          </div>
        </div>

        {/* Categories */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
            Program Categories *
          </label>
          <div className="flex flex-wrap gap-2">
            {(['Merit-Based', 'Need-Based', 'Research', 'Minority', 'STEM', 'Arts & Humanities'] as ScholarshipCategory[]).map((cat) => {
              const active = categories.includes(cat);
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => toggleCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors border ${
                    active
                      ? 'bg-emerald-600 border-emerald-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>

        {/* Regions & Eligible Roles */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Regions (Comma separated)
            </label>
            <input
              type="text"
              value={regionsInput}
              onChange={(e) => setRegionsInput(e.target.value)}
              placeholder="National, State-Level, Regional"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Eligible User Roles (Comma separated)
            </label>
            <input
              type="text"
              value={eligibleRolesInput}
              onChange={(e) => setEligibleRolesInput(e.target.value)}
              placeholder="STUDENT, RESEARCHER"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Tags & Required Documents */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Search Tags (Comma separated)
            </label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="Merit, STEM, Grant"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Required Verifiable Documents
            </label>
            <input
              type="text"
              value={documentsInput}
              onChange={(e) => setDocumentsInput(e.target.value)}
              placeholder="Income Certificate, Caste Certificate, Marksheets"
              className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs md:text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100 dark:border-slate-800">
          <button
            type="button"
            onClick={() => navigate('/scholarships')}
            disabled={isSubmitting}
            className="px-4 py-2.5 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-colors shadow-md flex items-center space-x-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{isSubmitting ? 'Saving Program...' : isEdit ? 'Update Scholarship' : 'Create Scholarship Draft'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
