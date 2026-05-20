import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ChatService, ChatMessage } from './chat.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    MatCardModule, 
    MatInputModule, 
    MatButtonModule, 
    MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements AfterViewChecked {
  title = '401(k) Withdrawal Assistant';
  
  messages: ChatMessage[] = [];
  newMessage: string = '';
  isLoading: boolean = false;

  @ViewChild('scrollMe') private myScrollContainer!: ElementRef;

  constructor(private chatService: ChatService) {}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.myScrollContainer.nativeElement.scrollTop = this.myScrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  sendMessage() {
    if (!this.newMessage.trim()) return;

    const userMessage = this.newMessage;
    this.messages.push({ role: 'user', content: userMessage });
    this.newMessage = '';
    this.isLoading = true;

    // We pass a copy of history up to this point
    const history = this.messages.slice(0, -1);

    this.chatService.sendMessage(userMessage, history).subscribe({
      next: (res) => {
        this.messages.push({ role: 'assistant', content: res.response });
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.messages.push({ 
          role: 'assistant', 
          content: 'Sorry, there was an error processing your request. Ensure the FastAPI backend is running.' 
        });
        this.isLoading = false;
      }
    });
  }
}
