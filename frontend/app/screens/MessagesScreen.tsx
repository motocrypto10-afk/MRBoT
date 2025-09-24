import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Share,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

interface Message {
  id: string;
  meeting_id: string;
  content: string;
  type: 'highlight' | 'decision' | 'action_item';
  created_at: string;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function MessagesScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchMessages = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/messages`);
      const data = await response.json();
      setMessages(data);
    } catch (error) {
      console.error('Error fetching messages:', error);
      Alert.alert('Error', 'Failed to load messages');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchMessages();
  };

  const shareMessage = async (message: Message) => {
    try {
      await Share.share({
        message: `Meeting Highlight:\n\n${message.content}`,
        title: 'Meeting Highlight',
      });
    } catch (error) {
      console.error('Error sharing message:', error);
      Alert.alert('Error', 'Failed to share message');
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'decision':
        return 'checkmark-circle';
      case 'action_item':
        return 'radio-button-off';
      default:
        return 'star';
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'decision':
        return '#34C759';
      case 'action_item':
        return '#007AFF';
      default:
        return '#FF9500';
    }
  };

  const getMessageTypeLabel = (type: string) => {
    switch (type) {
      case 'decision':
        return 'Decision';
      case 'action_item':
        return 'Action Item';
      default:
        return 'Highlight';
    }
  };

  const renderMessageCard = ({ item }: { item: Message }) => (
    <View style={styles.messageCard}>
      <View style={styles.messageHeader}>
        <View style={styles.messageInfo}>
          <Ionicons
            name={getMessageIcon(item.type)}
            size={20}
            color={getMessageColor(item.type)}
          />
          <View style={styles.messageDetails}>
            <Text style={[
              styles.messageTypeText,
              { color: getMessageColor(item.type) }
            ]}>
              {getMessageTypeLabel(item.type)}
            </Text>
            <Text style={styles.messageTime}>
              {new Date(item.created_at).toLocaleDateString()} at{' '}
              {new Date(item.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Text>
          </View>
        </View>
        <TouchableOpacity
          style={styles.shareButton}
          onPress={() => shareMessage(item)}
        >
          <Ionicons name="share-outline" size={20} color="#007AFF" />
        </TouchableOpacity>
      </View>
      
      <Text style={styles.messageContent}>{item.content}</Text>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading messages...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={messages}
        renderItem={renderMessageCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="chatbubbles-outline" size={64} color="#C7C7CC" />
            <Text style={styles.emptyTitle}>No messages yet</Text>
            <Text style={styles.emptySubtitle}>
              Meeting highlights and key points will appear here for easy sharing
            </Text>
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
  },
  messageCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  messageInfo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    flex: 1,
  },
  messageDetails: {
    marginLeft: 8,
    flex: 1,
  },
  messageTypeText: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 2,
  },
  messageTime: {
    fontSize: 11,
    color: '#8E8E93',
  },
  shareButton: {
    padding: 4,
  },
  messageContent: {
    fontSize: 14,
    color: '#000',
    lineHeight: 20,
    backgroundColor: '#F8F9FA',
    padding: 12,
    borderRadius: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#E5E5EA',
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
});