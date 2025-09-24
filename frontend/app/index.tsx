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

interface Meeting {
  _id: string;
  title: string;
  date: string;
  summary: string;
  actionItemsCount: number;
  status: string;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function Index() {
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

  const onRefresh = () => {
    setRefreshing(true);
    fetchMeetings();
  };

  const startRecording = async () => {
    try {
      // Create a new meeting
      const response = await fetch(`${BACKEND_URL}/api/meetings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: `Meeting ${new Date().toLocaleString()}`,
        }),
      });
      
      if (response.ok) {
        const meeting = await response.json();
        Alert.alert('Meeting Created', `Meeting "${meeting.title}" has been created and will be processed.`);
        fetchMeetings();
      } else {
        throw new Error('Failed to create meeting');
      }
    } catch (error) {
      console.error('Error creating meeting:', error);
      Alert.alert('Error', 'Failed to create meeting');
    }
  };

  const renderMeetingCard = ({ item }: { item: Meeting }) => (
    <TouchableOpacity style={styles.meetingCard} onPress={() => {}}>
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
          <Text style={styles.loadingText}>Loading BotMR...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>BotMR</Text>
        <Text style={styles.headerSubtitle}>Meeting Recorder & Summarizer</Text>
      </View>

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
          </View>
        }
      />

      {/* Floating Record Button */}
      <TouchableOpacity style={styles.floatingButton} onPress={startRecording}>
        <Ionicons name="mic" size={28} color="#FFFFFF" />
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#8E8E93',
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
    paddingBottom: 100,
  },
  meetingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
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
    fontSize: 14,
    color: '#48484A',
    lineHeight: 20,
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  actionItemsCount: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#48484A',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
  floatingButton: {
    position: 'absolute',
    bottom: 30,
    right: 30,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
});