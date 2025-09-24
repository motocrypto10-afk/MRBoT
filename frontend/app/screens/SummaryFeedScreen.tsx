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
  status: string;
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
        summary: meeting.summary || 'Processing...',
        actionItemsCount: meeting.action_items?.length || 0,
        status: meeting.status,
      })));
    } catch (error) {
      console.error('Error fetching meetings:', error);
      Alert.alert('Error', 'Failed to load meetings');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
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
    // Navigate to recording screen
    (navigation as any).navigate('Record');
  };

  const viewMeetingDetails = (meetingId: string) => {
    // Navigate to MoM tab with the specific meeting
    (navigation as any).navigate('MoM', { meetingId });
  };

  const renderMeetingCard = ({ item }: { item: Meeting }) => (
    <TouchableOpacity 
      style={styles.meetingCard} 
      onPress={() => viewMeetingDetails(item._id)}
      activeOpacity={0.7}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.meetingTitle}>{item.title}</Text>
        <Text style={styles.meetingDate}>{item.date}</Text>
      </View>
      <Text style={styles.meetingSummary} numberOfLines={3}>
        {item.summary}
      </Text>
      <View style={styles.cardFooter}>
        <Text style={styles.actionItemsCount}>
          {item.actionItemsCount} action items
        </Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>
      
      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity 
          style={styles.quickActionButton}
          onPress={(e) => {
            e.stopPropagation();
            (navigation as any).navigate('Tasks');
          }}
        >
          <Ionicons name="checkmark-circle-outline" size={16} color="#007AFF" />
          <Text style={styles.quickActionText}>Tasks</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.quickActionButton}
          onPress={(e) => {
            e.stopPropagation();
            (navigation as any).navigate('Messages');
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
    </TouchableOpacity>
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#34C759';
      case 'processing':
        return '#FF9500';
      case 'pending':
        return '#007AFF';
      default:
        return '#8E8E93';
    }
  };

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

      {/* Floating Record Button - Central FAB */}
      <TouchableOpacity style={styles.floatingButton} onPress={startRecording}>
        <View style={styles.micButtonInner}>
          <Ionicons name="mic" size={28} color="#FFFFFF" />
        </View>
      </TouchableOpacity>
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
    paddingBottom: 120, // Extra padding for FAB
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
  },
  meetingDate: {
    fontSize: 14,
    color: '#8E8E93',
  },
  meetingSummary: {
    fontSize: 15,
    color: '#48484A',
    lineHeight: 22,
    marginBottom: 16,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  actionItemsCount: {
    fontSize: 13,
    color: '#007AFF',
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
    textTransform: 'capitalize',
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
  floatingButton: {
    position: 'absolute',
    bottom: 90, // Position above tab bar
    alignSelf: 'center',
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 12,
  },
  micButtonInner: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#FFFFFF',
  },
});