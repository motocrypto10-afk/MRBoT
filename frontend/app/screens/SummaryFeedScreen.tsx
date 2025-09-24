import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

interface Meeting {
  _id: string;
  title: string;
  date: string;
  summary: string;
  actionItemsCount: number;
  status: 'pending_upload' | 'processing' | 'completed' | 'pending';
  isNew?: boolean;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function SummaryFeedScreen() {
  const navigation = useNavigation();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/meetings`);
      const data = await response.json();
      setMeetings(data.map((meeting: any) => ({
        _id: meeting.id,
        title: meeting.title,
        date: meeting.date,
        summary: meeting.summary || getProcessingMessage(meeting.status),
        actionItemsCount: meeting.action_items?.length || 0,
        status: meeting.status || 'pending',
        isNew: isRecentMeeting(meeting.created_at),
      })));
    } catch (error) {
      console.error('Error fetching meetings:', error);
      Alert.alert('Error', 'Failed to load meetings');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getProcessingMessage = (status: string) => {
    switch (status) {
      case 'pending_upload':
        return 'Awaiting network...';
      case 'processing':
        return 'Transcribing & analyzing...';
      case 'completed':
        return '';
      default:
        return 'Processing...';
    }
  };

  const isRecentMeeting = (createdAt: string) => {
    const meetingTime = new Date(createdAt).getTime();
    const now = new Date().getTime();
    return (now - meetingTime) < 5 * 60 * 1000; // 5 minutes
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  // Focus event listener to refresh when tab is focused
  React.useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      fetchMeetings();
    });
    return unsubscribe;
  }, [navigation]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchMeetings();
  };

  const startRecording = () => {
    navigation.navigate('Record' as never);
  };

  const viewMeetingDetails = (meetingId: string) => {
    navigation.navigate('MoM' as never, { meetingId });
  };

  const renderStatusChip = (status: string, actionItemsCount: number) => {
    const getStatusConfig = () => {
      switch (status) {
        case 'pending_upload':
          return {
            color: '#FF9500',
            text: 'Awaiting network...',
            icon: 'cloud-upload-outline',
          };
        case 'processing':
          return {
            color: '#007AFF',
            text: 'Transcribing & analyzing...',
            icon: 'sync-outline',
          };
        case 'completed':
          return {
            color: '#34C759',
            text: `${actionItemsCount} Action Items • Summary Ready`,
            icon: 'checkmark-circle',
          };
        default:
          return {
            color: '#8E8E93',
            text: 'Processing...',
            icon: 'time-outline',
          };
      }
    };

    const config = getStatusConfig();
    
    return (
      <View style={[styles.statusChip, { backgroundColor: config.color }]}>
        <Ionicons name={config.icon as any} size={12} color="#FFFFFF" />
        <Text style={styles.statusChipText}>{config.text}</Text>
      </View>
    );
  };

  const renderMeetingCard = ({ item }: { item: Meeting }) => (
    <TouchableOpacity 
      style={[styles.meetingCard, item.isNew && styles.newMeetingCard]} 
      onPress={() => viewMeetingDetails(item._id)}
      activeOpacity={0.7}
    >
      {item.isNew && (
        <View style={styles.newBadge}>
          <Text style={styles.newBadgeText}>NEW</Text>
        </View>
      )}

      <View style={styles.cardHeader}>
        <Text style={styles.meetingTitle}>{item.title}</Text>
        <Text style={styles.meetingDate}>{item.date}</Text>
      </View>

      {/* Status Chip */}
      {renderStatusChip(item.status, item.actionItemsCount)}
      
      {/* Summary or Processing Message */}
      {item.status === 'completed' && item.summary && (
        <Text style={styles.meetingSummary} numberOfLines={3}>
          {item.summary}
        </Text>
      )}
      
      {/* Quick Actions - Only show for completed meetings */}
      {item.status === 'completed' && (
        <View style={styles.quickActions}>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={(e) => {
              e.stopPropagation();
              navigation.navigate('Tasks' as never);
            }}
          >
            <Ionicons name="checkmark-circle-outline" size={16} color="#007AFF" />
            <Text style={styles.quickActionText}>Tasks</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={(e) => {
              e.stopPropagation();
              navigation.navigate('Messages' as never);
            }}
          >
            <Ionicons name="chatbubbles-outline" size={16} color="#007AFF" />
            <Text style={styles.quickActionText}>Share</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={(e) => {
              e.stopPropagation();
              viewMeetingDetails(item._id);
            }}
          >
            <Ionicons name="document-text-outline" size={16} color="#007AFF" />
            <Text style={styles.quickActionText}>Full MoM</Text>
          </TouchableOpacity>
        </View>
      )}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading meetings...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={meetings}
        renderItem={renderMeetingCard}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="mic-outline" size={64} color="#C7C7CC" />
            <Text style={styles.emptyTitle}>Welcome to BotMR</Text>
            <Text style={styles.emptySubtitle}>
              Record meetings, get AI-powered summaries, tasks, and insights
            </Text>
            <TouchableOpacity style={styles.getStartedButton} onPress={startRecording}>
              <Text style={styles.getStartedText}>Start Recording</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#8E8E93',
  },
  listContainer: {
    padding: 16,
    paddingBottom: 20,
  },
  meetingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
    position: 'relative',
  },
  newMeetingCard: {
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  newBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: '#007AFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  newBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  meetingTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    flex: 1,
    marginRight: 40, // Space for NEW badge
  },
  meetingDate: {
    fontSize: 14,
    color: '#8E8E93',
  },
  statusChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    marginBottom: 12,
    alignSelf: 'flex-start',
  },
  statusChipText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 4,
  },
  meetingSummary: {
    fontSize: 15,
    color: '#48484A',
    lineHeight: 22,
    marginBottom: 16,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 12,
    borderTopWidth: 0.5,
    borderTopColor: '#E5E5EA',
  },
  quickActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  quickActionText: {
    fontSize: 13,
    color: '#007AFF',
    fontWeight: '500',
    marginLeft: 6,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#000',
    marginTop: 20,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    paddingHorizontal: 40,
    lineHeight: 24,
    marginBottom: 32,
  },
  getStartedButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 25,
  },
  getStartedText: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});