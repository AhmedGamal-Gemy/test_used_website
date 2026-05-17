import { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Button from '../components/Button';
import Input from '../components/Input';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';
import { messagesAPI, laptopsAPI, partsAPI, servicesAPI } from '../api';
import { useToast } from '../hooks/useToast';

const LISTING_TYPES = [
  { value: 'laptop', label: 'Laptop' },
  { value: 'part', label: 'Part' },
  { value: 'service', label: 'Service' },
];

export default function Messages() {
  const { user, isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showSuccess, showError } = useToast();

  // Initial params from URL (e.g. from "Contact Us" button on listing detail)
  const initialListingId = searchParams.get('listing') || '';
  const initialListingType = searchParams.get('type') || '';

  const [activeTab, setActiveTab] = useState(initialListingId ? 'inquiries' : 'inquiries');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // User's conversations
  const [conversations, setConversations] = useState([]);
  const [selectedConv, setSelectedConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);

  // Admin: all conversations
  const [adminConversations, setAdminConversations] = useState([]);
  const [selectedAdminConv, setSelectedAdminConv] = useState(null);
  const [adminMessages, setAdminMessages] = useState([]);
  const [adminReplyText, setAdminReplyText] = useState('');
  const [adminSending, setAdminSending] = useState(false);

  // New inquiry form
  const [inquiryForm, setInquiryForm] = useState({
    listingType: initialListingType || 'laptop',
    listingId: initialListingId,
    listingTitle: '',
    content: '',
  });
  const [submittingInquiry, setSubmittingInquiry] = useState(false);
  const [listings, setListings] = useState([]);
  const [listingsLoading, setListingsLoading] = useState(false);
  const [listingSearch, setListingSearch] = useState('');

  const messagesEndRef = useRef(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [authLoading, isAuthenticated, navigate]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Fetch conversations on mount
  useEffect(() => {
    if (isAuthenticated) {
      if (isAdmin) {
        fetchAdminConversations();
      } else {
        fetchConversations();
      }
    }
  }, [isAuthenticated, isAdmin]);

  // Load initial listing title if provided via URL
  useEffect(() => {
    if (initialListingId && initialListingType) {
      loadListingTitle(initialListingId, initialListingType);
    }
  }, [initialListingId, initialListingType]);

  // If initial listing provided, auto-select it
  useEffect(() => {
    if (initialListingId && conversations.length > 0) {
      const conv = conversations.find(
        c => c.listing_id === initialListingId && c.listing_type === initialListingType
      );
      if (conv) {
        handleSelectConversation(conv);
      }
    }
  }, [conversations, initialListingId, initialListingType]);

  async function loadListingTitle(listingId, listingType) {
    try {
      const apiMap = { laptop: laptopsAPI, part: partsAPI, service: servicesAPI };
      const api = apiMap[listingType];
      if (!api) return;
      const res = await api.get(listingId);
      const data = res.data?.data || res.data;
      const title = data.title || 'Unknown Listing';
      setInquiryForm(prev => ({ ...prev, listingTitle: title }));
    } catch {
      // ignore
    }
  }

  async function fetchConversations() {
    setLoading(true);
    setError(null);
    try {
      const res = await messagesAPI.getConversations();
      setConversations(res.data || []);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
      setError('Failed to load conversations.');
    } finally {
      setLoading(false);
    }
  }

  async function fetchAdminConversations() {
    setLoading(true);
    setError(null);
    try {
      const res = await messagesAPI.getAdminConversations();
      setAdminConversations(res.data || []);
    } catch (err) {
      console.error('Failed to fetch admin conversations:', err);
      setError('Failed to load inquiries.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectConversation(conv) {
    setSelectedConv(conv);
    setMessagesLoading(true);
    try {
      const res = await messagesAPI.getConversation({
        listing_id: conv.listing_id,
        listing_type: conv.listing_type,
      });
      setMessages(res.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch conversation:', err);
      setError('Failed to load messages.');
      setMessages([]);
    } finally {
      setMessagesLoading(false);
    }
  }

  async function handleSelectAdminConversation(conv) {
    setSelectedAdminConv(conv);
    setMessagesLoading(true);
    try {
      const res = await messagesAPI.getAdminConversation({
        listing_id: conv.listing_id,
        listing_type: conv.listing_type,
      });
      setAdminMessages(res.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch admin conversation:', err);
      setError('Failed to load messages.');
      setAdminMessages([]);
    } finally {
      setMessagesLoading(false);
    }
  }

  async function handleAdminReply(e) {
    e.preventDefault();
    if (!adminReplyText.trim() || !selectedAdminConv) return;
    setAdminSending(true);
    try {
      await messagesAPI.adminReply({
        listing_id: selectedAdminConv.listing_id,
        listing_type: selectedAdminConv.listing_type,
        content: adminReplyText.trim(),
      });
      setAdminReplyText('');
      showSuccess('Reply sent!');
      // Refresh
      await handleSelectAdminConversation(selectedAdminConv);
      await fetchAdminConversations();
    } catch (err) {
      showError('Failed to send reply.');
    } finally {
      setAdminSending(false);
    }
  }

  // New inquiry
  async function handleListingTypeChange(type) {
    setInquiryForm(prev => ({ ...prev, listingType: type, listingId: '', listingTitle: '' }));
    setListings([]);
    setListingSearch('');
  }

  async function searchListings(query) {
    setListingSearch(query);
    if (!query.trim() || !inquiryForm.listingType) return;
    setListingsLoading(true);
    try {
      const apiMap = { laptop: laptopsAPI, part: partsAPI, service: servicesAPI };
      const api = apiMap[inquiryForm.listingType];
      if (!api) return;
      const res = await api.list({ search: query, limit: 10 });
      const data = res.data?.data || res.data || [];
      setListings(Array.isArray(data) ? data : []);
    } catch {
      setListings([]);
    } finally {
      setListingsLoading(false);
    }
  }

  function selectListing(listing) {
    setInquiryForm(prev => ({
      ...prev,
      listingId: listing.id || listing._id,
      listingTitle: listing.title,
    }));
    setListings([]);
    setListingSearch('');
  }

  async function handleSubmitInquiry(e) {
    e.preventDefault();
    if (!inquiryForm.content.trim() || !inquiryForm.listingId) return;
    setSubmittingInquiry(true);
    try {
      await messagesAPI.sendInquiry({
        listing_id: inquiryForm.listingId,
        listing_type: inquiryForm.listingType,
        content: inquiryForm.content.trim(),
      });
      showSuccess('Inquiry sent! We\'ll get back to you soon.');
      setInquiryForm({ listingType: 'laptop', listingId: '', listingTitle: '', content: '' });
      setActiveTab('inquiries');
      fetchConversations();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to send inquiry.');
    } finally {
      setSubmittingInquiry(false);
    }
  }

  const currentUserId = user?._id || user?.id;

  if (authLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center"><Spinner size="lg" /></main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {isAdmin ? 'Customer Inquiries' : 'Contact Us'}
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">{error}</div>
        )}

        {isAdmin ? (
          /* ============ ADMIN VIEW ============ */
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden flex flex-col md:flex-row h-[600px]">
            {/* Left: conversation list */}
            <div className="w-full md:w-80 border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">
              <div className="p-4 border-b border-gray-200">
                <h2 className="font-semibold text-gray-900">All Inquiries ({adminConversations.length})</h2>
              </div>
              {loading ? (
                <div className="flex justify-center py-8"><Spinner /></div>
              ) : adminConversations.length === 0 ? (
                <div className="p-4"><EmptyState icon="inbox" title="No inquiries yet" description="Customer inquiries will appear here." /></div>
              ) : (
                adminConversations.map((conv) => (
                  <button
                    key={`${conv.listing_id}-${conv.listing_type}`}
                    onClick={() => handleSelectAdminConversation(conv)}
                    className={`w-full text-left p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      selectedAdminConv?.listing_id === conv.listing_id && selectedAdminConv?.listing_type === conv.listing_type
                        ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-medium text-gray-900 text-sm truncate pr-2">
                        {conv.listing_title || 'Unknown Listing'}
                      </h3>
                    </div>
                    <p className="text-xs text-gray-500 truncate">
                      From: {conv.sender_name || conv.sender_email || 'Unknown'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1 capitalize">{conv.listing_type}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{conv.message_count} message{conv.message_count !== 1 ? 's' : ''}</p>
                  </button>
                ))
              )}
            </div>

            {/* Right: messages + reply */}
            <div className="flex-1 flex flex-col min-w-0">
              {selectedAdminConv ? (
                <>
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-900">{selectedAdminConv.listing_title || 'Unknown Listing'}</h3>
                    <p className="text-xs text-gray-500">
                      From: {selectedAdminConv.sender_name || selectedAdminConv.sender_email || 'Unknown'} &middot; {selectedAdminConv.listing_type}
                    </p>
                  </div>
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messagesLoading ? (
                      <div className="flex justify-center py-8"><Spinner /></div>
                    ) : adminMessages.length === 0 ? (
                      <div className="flex items-center justify-center h-full"><p className="text-gray-500 text-sm">No messages yet.</p></div>
                    ) : (
                      adminMessages.map((msg) => {
                        const isAdminMsg = msg.is_admin_reply;
                        return (
                          <div key={msg.id} className="flex">
                            <div className={`max-w-xs px-4 py-2 ${
                              isAdminMsg
                                ? 'bg-blue-600 text-white rounded-lg rounded-br-none ml-auto'
                                : 'bg-gray-200 text-gray-900 rounded-lg rounded-bl-none'
                            }`}>
                              <p className="text-sm">{msg.content}</p>
                              <p className={`text-xs mt-1 ${isAdminMsg ? 'text-blue-100' : 'text-gray-500'}`}>
                                {msg.created_at ? new Date(msg.created_at).toLocaleString() : ''}
                                {isAdminMsg && ' (You)'}
                              </p>
                            </div>
                          </div>
                        );
                      })
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                  <form onSubmit={handleAdminReply} className="p-4 border-t border-gray-200">
                    <div className="flex gap-2">
                      <Input
                        value={adminReplyText}
                        onChange={(e) => setAdminReplyText(e.target.value)}
                        placeholder="Type your reply..."
                        className="flex-1"
                        disabled={adminSending}
                      />
                      <Button type="submit" variant="primary" disabled={!adminReplyText.trim() || adminSending} loading={adminSending}>
                        Reply
                      </Button>
                    </div>
                  </form>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <EmptyState icon="inbox" title="Select an inquiry" description="Choose an inquiry from the list to view and reply." />
                </div>
              )}
            </div>
          </div>
        ) : (
          /* ============ REGULAR USER VIEW ============ */
          <>
            {/* Tabs */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setActiveTab('inquiries')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'inquiries' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                My Inquiries
              </button>
              <button
                onClick={() => setActiveTab('new')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'new' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                New Inquiry
              </button>
            </div>

            {activeTab === 'inquiries' ? (
              /* My Inquiries Tab */
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden flex flex-col md:flex-row h-[550px]">
                {/* Left: conversation list */}
                <div className="w-full md:w-72 border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">
                  <div className="p-4 border-b border-gray-200">
                    <h2 className="font-semibold text-gray-900">Conversations</h2>
                  </div>
                  {loading ? (
                    <div className="flex justify-center py-8"><Spinner /></div>
                  ) : conversations.length === 0 ? (
                    <div className="p-4"><EmptyState icon="inbox" title="No inquiries" description="Send an inquiry about a listing." /></div>
                  ) : (
                    conversations.map((conv) => (
                      <button
                        key={`${conv.listing_id}-${conv.listing_type}`}
                        onClick={() => handleSelectConversation(conv)}
                        className={`w-full text-left p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                          selectedConv?.listing_id === conv.listing_id && selectedConv?.listing_type === conv.listing_type
                            ? 'bg-blue-50' : ''
                        }`}
                      >
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="font-medium text-gray-900 text-sm truncate pr-2">
                            {conv.listing_title || 'Unknown Listing'}
                          </h3>
                        </div>
                        {conv.last_message && (
                          <p className="text-xs text-gray-600 truncate">{conv.last_message}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1 capitalize">{conv.listing_type}</p>
                      </button>
                    ))
                  )}
                </div>

                {/* Right: message thread */}
                <div className="flex-1 flex flex-col min-w-0">
                  {selectedConv ? (
                    <>
                      <div className="p-4 border-b border-gray-200">
                        <h3 className="font-semibold text-gray-900">{selectedConv.listing_title || 'Unknown Listing'}</h3>
                        <p className="text-sm text-gray-500 capitalize">{selectedConv.listing_type}</p>
                      </div>
                      <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messagesLoading ? (
                          <div className="flex justify-center py-8"><Spinner /></div>
                        ) : messages.length === 0 ? (
                          <div className="flex items-center justify-center h-full"><p className="text-gray-500 text-sm">No messages yet.</p></div>
                        ) : (
                          messages.map((msg) => {
                            const isSent = msg.sender_id === currentUserId;
                            return (
                              <div key={msg.id} className="flex">
                                <div className={`max-w-xs px-4 py-2 ${
                                  isSent
                                    ? 'bg-blue-600 text-white rounded-lg rounded-br-none ml-auto'
                                    : 'bg-gray-200 text-gray-900 rounded-lg rounded-bl-none'
                                }`}>
                                  <p className="text-sm">{msg.content}</p>
                                  <p className={`text-xs mt-1 ${isSent ? 'text-blue-100' : 'text-gray-500'}`}>
                                    {msg.created_at ? new Date(msg.created_at).toLocaleString() : ''}
                                    {msg.is_admin_reply && !isSent && ' (Support)'}
                                  </p>
                                </div>
                              </div>
                            );
                          })
                        )}
                        <div ref={messagesEndRef} />
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <EmptyState icon="inbox" title="Select a conversation" description="Choose an inquiry to view the conversation." />
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* New Inquiry Tab */
              <div className="max-w-2xl mx-auto bg-white rounded-xl border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Send an Inquiry</h2>

                <form onSubmit={handleSubmitInquiry} className="space-y-4">
                  {/* Listing Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">About what?</label>
                    <div className="flex gap-2">
                      {LISTING_TYPES.map(lt => (
                        <button
                          key={lt.value}
                          type="button"
                          onClick={() => handleListingTypeChange(lt.value)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            inquiryForm.listingType === lt.value
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {lt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Listing Search/Select */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Which listing?
                    </label>
                    {inquiryForm.listingId ? (
                      <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <span className="text-sm text-blue-800 font-medium flex-1">{inquiryForm.listingTitle || inquiryForm.listingId}</span>
                        <button
                          type="button"
                          onClick={() => setInquiryForm(prev => ({ ...prev, listingId: '', listingTitle: '' }))}
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Change
                        </button>
                      </div>
                    ) : (
                      <div className="relative">
                        <input
                          type="text"
                          value={listingSearch}
                          onChange={(e) => searchListings(e.target.value)}
                          placeholder={`Search ${inquiryForm.listingType}s...`}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        />
                        {listingsLoading && (
                          <div className="absolute right-3 top-2.5"><Spinner size="sm" /></div>
                        )}
                        {listings.length > 0 && (
                          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                            {listings.map((l) => (
                              <button
                                key={l.id || l._id}
                                type="button"
                                onClick={() => selectListing(l)}
                                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 border-b border-gray-100 last:border-0"
                              >
                                <span className="font-medium">{l.title}</span>
                                {l.price && <span className="text-gray-500 ml-2">${l.price}</span>}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Message */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Your Message</label>
                    <textarea
                      value={inquiryForm.content}
                      onChange={(e) => setInquiryForm(prev => ({ ...prev, content: e.target.value }))}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      placeholder="Write your question or inquiry..."
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    disabled={!inquiryForm.content.trim() || !inquiryForm.listingId || submittingInquiry}
                    loading={submittingInquiry}
                  >
                    Send Inquiry
                  </Button>
                </form>
              </div>
            )}
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}
