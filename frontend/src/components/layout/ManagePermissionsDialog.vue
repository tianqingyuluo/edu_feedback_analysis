<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod";
// import { h, ref, watch } from "vue"; // h 不再需要，因为ElMessage通常只显示字符串
import { ref, watch } from "vue"; // h removed
import * as z from "zod";
import type { SubmissionHandler } from 'vee-validate';
// --- 导入 ElMessage ---
import { ElMessage } from 'element-plus';
// ----------------------
// 从 shadcn-vue 导入 UI 组件
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
// --- 导入 Pinia store ---
import { useUsersStore } from '@/store/usersStore.ts';
import type {UpdateUserRequest} from "@/types/users.ts";
const userStore = useUsersStore();
// 定义 Props 接口
interface Props {
  userId?: string;
  username?: string;
  phone?: string;
  permission?: string;
}
const props = withDefaults(defineProps<Props>(), {
  userId: '0',
  username: '',
  phone: '',
  permission: ''
});
// 定义原始的 Zod schema 对象
const rawPermissionSchema = z.object({
  username: z
      .string()
      .min(2, "用户名最少2个字符")
      .max(50, "用户名最多50个字符")
      .nonempty("用户名不能为空"),
  phone: z
      .string()
      .regex(/^1[3-9]\d{9}$/, "请输入有效的11位手机号")
      .nonempty("手机号不能为空"),
  password: z
      .string()
      .max(20, "密码最多20个字符"), // 留空表示不修改，所以不强制min
  permission: z
      .string()
      .nonempty("请选择权限")
});
// 将原始 Zod schema 转换为 VeeValidate 兼容的 TypedSchema
const permissionSchema = toTypedSchema(rawPermissionSchema);
// 表单初始值
const formInitialValues = ref({
  username: props.username,
  phone: props.phone,
  password: '', // 密码默认为空，用户可以选择是否修改
  permission: props.permission
});
// 监听 props 变化，更新表单初始值
watch(() => props, (newProps) => {
  formInitialValues.value = {
    username: newProps.username,
    phone: newProps.phone,
    password: '',
    permission: newProps.permission
  };
}, { deep: true });
const onSubmit: SubmissionHandler = async (values, actions) => {
  // ElMessage 不需要 loading 状态，它会立即显示。
  // 对于异步操作，考虑在按钮上显示加载状态。
  try {
    // 使用 Zod 验证数据
    const validatedValues = rawPermissionSchema.parse(values);
    // 构建更新请求对象
    const updateRequest: UpdateUserRequest = {
      username: validatedValues.username,
      phone: validatedValues.phone,
      // 如果密码字段为空，不发送 password 属性，让后端决定不更新密码
      password: validatedValues.password ,
      role: validatedValues.permission.toUpperCase()
    };
    // 调用 store 的更新方法，传入用户ID和更新数据
    const updatedUser = await userStore.updateUser(props.userId, updateRequest);
    // --- 替换为 ElMessage.success ---
    ElMessage.success({
      message: `用户 ${updatedUser.username} 信息更新成功！`,
    });
    isDialogOpen.value = false;
  } catch (error: any) {
    // --- 错误处理，只 log 和抛出，不显示 ElMessage.error ---
    if (error instanceof z.ZodError) {
      console.error("数据验证失败:", error);
      // 可以选择抛出更详细的错误信息，如果外部有需要
      throw new Error("数据验证失败，请检查输入的数据格式是否正确。");
    } else {
      console.error("更新用户信息失败:", error);
      throw new Error(error.message || "更新用户信息失败，请检查网络或稍后重试。");
    }
    // -----------------------------------------------------
  }
};
const isDialogOpen = ref(false)
</script>
<template>
  <Form v-slot="{ handleSubmit }" as="" keep-values :validation-schema="permissionSchema" :initial-values="formInitialValues">
    <Dialog v-model:open="isDialogOpen">
      <DialogTrigger as-child>
        <Button class="bg-blue-500 text-white text-xs hover:bg-blue-600 transition-colors py-2 px-3 rounded">
          管理权限
        </Button>
      </DialogTrigger>
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>管理用户信息</DialogTitle>
          <DialogDescription>
            修改用户信息（留空密码表示不修改）
            <span v-if="userId" class="text-gray-500 text-xs block mt-1">用户ID: {{ userId }}</span>
          </DialogDescription>
        </DialogHeader>
        <form id="managePermissionForm" @submit="handleSubmit($event, onSubmit)">
          <!-- 用户名字段 -->
          <FormField v-slot="{ componentField }" name="username">
            <FormItem class="mb-4">
              <FormLabel>用户名</FormLabel>
              <FormControl>
                <Input type="text" placeholder="请输入用户名" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>
          <!-- 手机号字段 -->
          <FormField v-slot="{ componentField }" name="phone">
            <FormItem class="mb-4">
              <FormLabel>手机号</FormLabel>
              <FormControl>
                <Input type="tel" placeholder="请输入11位手机号" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>
          <!-- 密码字段 -->
          <FormField v-slot="{ componentField }" name="password">
            <FormItem class="mb-4">
              <FormLabel>密码</FormLabel>
              <FormControl>
                <Input type="password" placeholder="留空表示不修改密码" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>
          <!-- 权限字段 -->
          <FormField v-slot="{ componentField }" name="permission">
            <FormItem class="mb-6">
              <FormLabel>权限级别</FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="请选择权限" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="OPERATOR">
                      操作员 (operator)
                    </SelectItem>
                    <SelectItem value="USER">
                      普通用户 (user)
                    </SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>
        </form>
        <DialogFooter>
          <Button type="submit" form="managePermissionForm">
            确定
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Form>
</template>