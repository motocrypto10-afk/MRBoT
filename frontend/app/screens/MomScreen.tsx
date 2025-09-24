import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

interface Meeting {
  id: string;
  title: string;
  date: string;
  summary?: string;
  transcript?: string;
  decisions: string[];
  action_items: string[];
  participants: string[];
  status: string;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function MomScreen() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expandedMeeting, setExpandedMeeting] = useState<string | null>(null);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/meetings`);
      const data = await response.json();
      setMeetings(data.filter((m: Meeting) => m.status === 'completed'));
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

  const toggleExpanded = (meetingId: string) => {
    setExpandedMeeting(expandedMeeting === meetingId ? null : meetingId);
  };

  const exportMeeting = (meeting: Meeting) => {
    Alert.alert(
      'Export Meeting',
      'Choose export format',
      [
        { text: 'PDF', onPress: () => console.log('Export as PDF') },
        { text: 'DOCX', onPress: () => console.log('Export as DOCX') },
        { text: 'Email', onPress: () => console.log('Send via Email') },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const renderMeetingCard = ({ item }: { item: Meeting }) => {
    const isExpanded = expandedMeeting === item.id;
    
    return (
      <View style={styles.meetingCard}>
        <TouchableOpacity 
          style={styles.cardHeader}
          onPress={() => toggleExpanded(item.id)}
        >
          <View style={styles.headerInfo}>
            <Text style={styles.meetingTitle}>{item.title}</Text>
            <Text style={styles.meetingDate}>{item.date}</Text>
          </View>
          <Ionicons
            name={isExpanded ? 'chevron-up' : 'chevron-down'}
            size={24}
            color="#8E8E93"
          />
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.expandedContent}>
            {/* Summary Section */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Summary</Text>
              <Text style={styles.sectionContent}>
                {item.summary || 'No summary available'}
              </Text>
            </View>

            {/* Decisions Section */}
            {item.decisions.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Key Decisions</Text>
                {item.decisions.map((decision, index) => (
                  <View key={index} style={styles.listItem}>
                    <Ionicons name="checkmark-circle-outline" size={16} color="#34C759" />
                    <Text style={styles.listItemText}>{decision}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Action Items Section */}
            {item.action_items.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Action Items</Text>
                {item.action_items.map((action, index) => (
                  <View key={index} style={styles.listItem}>
                    <Ionicons name="radio-button-off-outline" size={16} color="#007AFF" />
                    <Text style={styles.listItemText}>{action}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Participants Section */}
            {item.participants.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Participants</Text>
                <View style={styles.participantsContainer}>
                  {item.participants.map((participant, index) => (
                    <View key={index} style={styles.participantChip}>
                      <Text style={styles.participantText}>{participant}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}

            {/* Transcript Section */}
            {item.transcript && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Transcript</Text>
                <Text style={styles.transcriptText} numberOfLines={5}>
                  {item.transcript}
                </Text>
                <TouchableOpacity style={styles.readMoreButton}>
                  <Text style={styles.readMoreText}>Read Full Transcript</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Export Button */}
            <TouchableOpacity
              style={styles.exportButton}
              onPress={() => exportMeeting(item)}
            >
              <Ionicons name="share-outline" size={20} color="#007AFF" />
              <Text style={styles.exportButtonText}>Export</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
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
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="document-text-outline" size={64} color="#C7C7CC" />
            <Text style={styles.emptyTitle}>No meeting minutes yet</Text>
            <Text style={styles.emptySubtitle}>
              Complete meeting recordings will appear here as minutes
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
  meetingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
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
    padding: 16,
  },
  headerInfo: {
    flex: 1,
  },
  meetingTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  meetingDate: {
    fontSize: 14,
    color: '#8E8E93',
  },
  expandedContent: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E5EA',
    padding: 16,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
  },
  sectionContent: {
    fontSize: 14,
    color: '#48484A',
    lineHeight: 20,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  listItemText: {
    fontSize: 14,
    color: '#48484A',
    marginLeft: 8,
    flex: 1,
    lineHeight: 18,
  },
  participantsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  participantChip: {
    backgroundColor: '#E5E5EA',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  participantText: {
    fontSize: 12,
    color: '#48484A',
    fontWeight: '500',
  },
  transcriptText: {
    fontSize: 14,
    color: '#48484A',
    lineHeight: 20,
    fontStyle: 'italic',
  },
  readMoreButton: {
    marginTop: 8,
  },
  readMoreText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  exportButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F2F2F7',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  exportButtonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
    marginLeft: 8,
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